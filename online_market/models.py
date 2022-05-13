from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db import models

import random


class Comment(models.Model):
    VALIDATED = 'v'
    WAITING = 'w'
    REJECTED = 'r'
    COMMENT_STATUS = [
        (VALIDATED, 'Validated'),
        (WAITING, "Waiting to validate by Admin"),
        (REJECTED, 'Rejected by Admin')
    ]
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=COMMENT_STATUS, default=WAITING)

    def __str__(self):
        return self.content


class Product(models.Model):
    type = models.CharField(max_length=50)
    brand = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)
    comments = GenericRelation(Comment, related_query_name='comments')
    score = models.DecimalField(default=0, decimal_places=2, max_digits=3,
                                validators=[MinValueValidator(-5), MaxValueValidator(5)])
    vote_quantity = models.IntegerField(default=0)
    product_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"Type: {self.type}, Brand: {self.brand}, Name: {self.name}"


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.product.name


class ShopOrder(models.Model):
    REGISTERED = 'r'
    VERIFIED = 'v'
    SENT = 's'
    DELIVERED = 'd'
    ORDER_STATUS = [
        (REGISTERED, "Registered order"),
        (VERIFIED, "Verified by admin"),
        (SENT, "Sent"),
        (DELIVERED, "Delivered")
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    track_id = models.BigIntegerField()
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default=REGISTERED)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    @staticmethod
    def generate_track_id():
        return random.randrange(10**10, 10**11)

    def __str__(self):
        return str(self.track_id)
