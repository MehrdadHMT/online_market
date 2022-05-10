from django.shortcuts import get_object_or_404

from .models import Product


def check_product_existence(pid):
	try:
		Product.objects.get(pk=pid)
	except Product.DoesNotExist:
		return False

	return True


def check_product_quantity(pid, quantity):
	product = get_object_or_404(Product, pk=pid)
	if product.product_quantity < quantity:
		return False

	return True
