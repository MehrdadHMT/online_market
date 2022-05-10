from django.contrib import admin

from .models import Product, Comment, CartItem, ShopOrder

admin.site.register(Product)
admin.site.register(Comment)
admin.site.register(CartItem)
admin.site.register(ShopOrder)
