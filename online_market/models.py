from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models


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
    content = models.TextField()
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
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)
    comments = GenericRelation(Comment, related_query_name='comments')

    def __str__(self):
        return f"Type: {self.type}, Brand: {self.brand}, Name: {self.name}"
