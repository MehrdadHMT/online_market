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

		p = Product.objects.create(type='A1', brand='B1', name='C1')
		print('*'*50)
		print(p.id)

	def test_post_detail(self):
		url = ONLINE_MARKET_URL + 'products/'

		resp = self.client.get(url + '1/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

		self.client.credentials()
		unauthenticated_resp = self.client.get(url + '1/')
		self.assertEqual(unauthenticated_resp.status_code, status.HTTP_200_OK)

		bad_resp = self.client.get(url + '2/')
		self.assertEqual(bad_resp.status_code, status.HTTP_404_NOT_FOUND)
