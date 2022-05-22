from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import json

from user_auth.models import Token, User

ONLINE_MARKET_URL = "/api/v1/auth/"


class RegisterViewTestCase(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_register(self):
		url = ONLINE_MARKET_URL + 'register/'

		bad_resp = self.client.post(url, dict(
			username="",
			password1="",
			password2="",
			email="",
			first_name="",
			last_name="",
			phone_number="",
			profile_image=""
		))
		self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

		# Password entirely numeric
		bad_resp = self.client.post(url, dict(
			username="test1",
			password1="12345",
			password2="12345",
			email="test1@mobin.com",
			first_name="",
			last_name="",
			phone_number="",
			profile_image=""
		))
		self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

		resp = self.client.post(url, dict(
			username="test1",
			password1="Mobin12345",
			password2="Mobin12345",
			email="test1@mobin.com",
			first_name="",
			last_name="",
			phone_number="",
			profile_image=""
		))
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

		# Repetitive username
		bad_resp = self.client.post(url, dict(
			username="test1",
			password1="Mobin12345",
			password2="Mobin12345",
			email="test2@mobin.com",
			first_name="",
			last_name="",
			phone_number="",
			profile_image=""
		))
		self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

		# Repetitive email
		bad_resp = self.client.post(url, dict(
			username="test.1",
			password1="Mobin12345",
			password2="Mobin12345",
			email="test1@mobin.com",
			first_name="",
			last_name="",
			phone_number="",
			profile_image=""
		))
		self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_login(self):
		url = ONLINE_MARKET_URL + 'login/'
		u = User.objects.create(username="Mehrdad", email="mehrdad@mobin.com")
		u.set_password("Mehrdad1234")
		u.save()

		# Empty fields
		bad_resp = self.client.post(url, {"username": "", "password": ""})
		self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

		# Fake username
		bad_resp = self.client.post(url, {"username": "mammad", "password": ""})
		self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

		# Incorrect password
		bad_resp = self.client.post(url, {"username": "Mehrdad", "password": "majid216"})
		self.assertEqual(bad_resp.status_code, status.HTTP_403_FORBIDDEN)

		resp = self.client.post(url, {"username": u.username, "password": "Mehrdad1234"})
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

	def test_logout(self):
		url = ONLINE_MARKET_URL + 'logout/'
		u = User.objects.create(username="Mehrdad", password="Mehrdad1234", email="mehrdad@mobin.com")
		token = Token.objects.create(user=u)
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

		auth_user_resp = self.client.get(url)
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)

		self.client.credentials()
		anon_user_resp = self.client.get(url)
		self.assertEqual(anon_user_resp.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_change_password(self):
		url = ONLINE_MARKET_URL + 'change-password/'
		u = User.objects.create(username="Mehrdad", email="mehrdad@mobin.com")
		u.set_password("Mehrdad1234")
		u.save()
		token = Token.objects.create(user=u)
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

		auth_user_resp = self.client.post(
			url,
			dict(
				old_pass="Mehrdad1234",
				new_pass="Mehrdad12345",
				new_pass_repeat="Mehrdad12345"
			)
		)
		print('*' * 50)
		print(auth_user_resp.data)
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)

		# Wrong password
		bad_resp = self.client.post(
			url,
			dict(
				old_pass="Mehrdad1234",
				new_pass="Mehrdad123",
				new_pass_repeat="Mehrdad123"
			)
		)
		self.assertEqual(bad_resp.status_code, status.HTTP_401_UNAUTHORIZED)

		# New passwords are not match
		bad_resp = self.client.post(
			url,
			dict(
				old_pass="Mehrdad1234",
				new_pass="Mehrdad123",
				new_pass_repeat="Mehrdad132"
			)
		)
		self.assertEqual(bad_resp.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileViewTestCase(TestCase):
	def setUp(self):
		u = User.objects.create(username="Mehrdad", email="mehrdad@mobin.com")
		u.set_password("Mehrdad1234")
		u.save()
		self.client = APIClient()
		token = Token.objects.create(user=u)
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

	def test_get_profile(self):
		url = ONLINE_MARKET_URL + 'get-profile/'

		auth_user_resp = self.client.get(url)
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)

		self.client.credentials()
		anon_user_resp = self.client.get(url)
		self.assertEqual(anon_user_resp.status_code, status.HTTP_401_UNAUTHORIZED)

		self.client.credentials(HTTP_AUTHORIZATION="Token 354354sdf3543dsf4g35dfgas54sadflkjasdf65")
		inv_token_resp = self.client.get(url)
		self.assertEqual(inv_token_resp.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_set_profile(self):
		url = ONLINE_MARKET_URL + 'set-profile/'

		auth_user_resp = self.client.patch(url, dict(
			first_name="mehrdad",
			last_name="b",
			phone_number="09369911546",
			profile_image=""
		))
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)

		inv_phone_number_resp = self.client.patch(url, dict(
			first_name="",
			last_name="",
			phone_number="65478",
			profile_image=""
		))
		self.assertEqual(inv_phone_number_resp.status_code, status.HTTP_400_BAD_REQUEST)

		inv_phone_number_resp = self.client.patch(url, dict(
			first_name="",
			last_name="",
			phone_number="09365421324697234654",
			profile_image=""
		))
		self.assertEqual(inv_phone_number_resp.status_code, status.HTTP_400_BAD_REQUEST)

		self.client.credentials()
		anon_user_resp = self.client.patch(url, dict(
			first_name="",
			last_name="",
			phone_number="",
			profile_image=""
		))
		self.assertEqual(anon_user_resp.status_code, status.HTTP_401_UNAUTHORIZED)

		self.client.credentials(HTTP_AUTHORIZATION="Token 354354sdf3543dsf4g35dfgas54sadflkjasdf65")
		inv_token_resp = self.client.patch(url, dict(
			first_name="",
			last_name="",
			phone_number="",
			profile_image=""
		))
		self.assertEqual(inv_token_resp.status_code, status.HTTP_401_UNAUTHORIZED)
