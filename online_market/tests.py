from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from user_auth.models import Token, User
from online_market.models import Product


ONLINE_MARKET_URL = "/api/v1/online-market/"


class ProductViewTestCase(TestCase):
	def setUp(self):
		self.admin_user = User.objects.create_superuser(username='admin', password='admin1234', email='admin@test.com')
		self.client = APIClient()
		token = Token.objects.create(user=self.admin_user)
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

		products = [
			Product.objects.create(
				type='type1',
				brand='brand1',
				name='name1',
			),
			Product.objects.create(
				type='type2',
				brand='brand2',
				name='name2',
			),
		]

		self.product_lookup = {p.id: p for p in products}

	def test_get_list(self):
		self.client.credentials()
		resp = self.client.get(ONLINE_MARKET_URL + "products/")
		data = resp.json()["results"]
		self.assertEqual(len(data), 2)

		self.assertEqual(resp.status_code, status.HTTP_200_OK)

	def test_add_product(self):
		url = ONLINE_MARKET_URL + "products/"

		empty_post_resp = self.client.post(url, {})
		self.assertEqual(empty_post_resp.status_code, status.HTTP_400_BAD_REQUEST)

		empty_product_dict = {
			"type": "",
			"brand": "",
			"name": ""
		}
		bad_resp = self.client.post(url, empty_product_dict)
		self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

		product_dict = {
			"type": "a1",
			"brand": "b1",
			"name": "c1"
		}
		resp = self.client.post(url, product_dict)
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Product.objects.all().count() == 3)

		duplicate_product_resp = self.client.post(url, product_dict)
		self.assertEqual(duplicate_product_resp.status_code, status.HTTP_400_BAD_REQUEST)

		self.client.credentials()
		unauthenticated_resp = self.client.post(url, {})
		self.assertEqual(unauthenticated_resp.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductDetailViewTestCase(TestCase):
	def setUp(self):
		self.u = User.objects.create(username='user', password='user1234', email='user@test.com')
		self.client = APIClient()
		token = Token.objects.create(user=self.u)
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

		self.p = Product.objects.create(type='A1', brand='B1', name='C1')

	def test_post_detail(self):
		url = ONLINE_MARKET_URL + 'products/'

		resp = self.client.get(url + f'{self.p.id}/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

		self.client.credentials()
		unauthenticated_resp = self.client.get(url + f'{self.p.id}/')
		self.assertEqual(unauthenticated_resp.status_code, status.HTTP_200_OK)

		bad_resp = self.client.get(url + '2/')
		self.assertEqual(bad_resp.status_code, status.HTTP_404_NOT_FOUND)


class ScoreViewTestCase(TestCase):
	def setUp(self):
		self.u = User.objects.create(username='user', password='user1234', email='user@test.com')
		token = Token.objects.create(user=self.u)
		self.client = APIClient()
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

		self.p = Product.objects.create(type='A1', brand='B1', name='C1', score=1, vote_quantity=5)

	def test_get_score(self):
		url = ONLINE_MARKET_URL + 'score/'

		auth_user_resp = self.client.get(url + f'{self.p.id}/')
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)

		self.client.credentials()
		anon_user_resp = self.client.get(url + f'{self.p.id}/')
		self.assertEqual(anon_user_resp.status_code, status.HTTP_200_OK)

	def test_set_score(self):
		url = ONLINE_MARKET_URL + 'score/'

		auth_user_resp = self.client.patch(url + f'{self.p.id}/', {"score": 4})
		pr = Product.objects.get(pk=self.p.id)
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)
		self.assertTrue(pr.score == 1.5)
		self.assertTrue(pr.vote_quantity == 6)

		self.client.credentials()
		anon_user_resp = self.client.patch(url + f'{self.p.id}/', {"score": 4})
		self.assertEqual(anon_user_resp.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentListViewTestCase(TestCase):
	def setUp(self):
		self.u1 = User.objects.create(username='user1', password='user1234', email='user1@test.com')
		token = Token.objects.create(user=self.u1)
		self.u2 = User.objects.create(username='user2', password='user12345', email='user2@test.com')
		self.client = APIClient()
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

		self.p = Product.objects.create(type='A1', brand='B1', name='C1')
		self.p.comments.create(user=self.u1, content='test1')
		self.p.comments.create(user=self.u2, content='test1', status='v')

	def test_comment_list(self):
		url = ONLINE_MARKET_URL + f'opinion/{self.p.id}/'

		auth_user_resp = self.client.get(url)
		data = auth_user_resp.json()['results']
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)
		self.assertTrue(len(data) == 1)

		self.client.credentials()
		anon_user_resp = self.client.get(url)
		self.assertEqual(anon_user_resp.status_code, status.HTTP_401_UNAUTHORIZED)

		admin_user = User.objects.create_superuser(username='admin', password='admin1234', email='admin@test.com')
		token = Token.objects.create(user=admin_user)
		self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

		admin_user_resp = self.client.get(url)
		data = admin_user_resp.json()['results']
		self.assertEqual(admin_user_resp.status_code, status.HTTP_200_OK)
		self.assertTrue(len(data) == 2)

	def test_comment_create(self):
		url = ONLINE_MARKET_URL + f'opinion/'

		auth_user_resp = self.client.post(url, {"id": self.p.id, "content": "test1"})
		self.assertEqual(auth_user_resp.status_code, status.HTTP_200_OK)

		self.client.credentials()
		anon_user_resp = self.client.post(url, {"id": self.p.id, "content": "test2"})
		self.assertEqual(anon_user_resp.status_code, status.HTTP_401_UNAUTHORIZED)

