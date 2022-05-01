from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import serializers

from user_auth.serializers import UserSerializer
from .models import Product, Comment


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "creator", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        readonly = ['created_at', 'modified_at']


class ProductDetailSerializer(ProductSerializer):
    comments = CommentSerializer(many=True, permissions=IsAuthenticated)

    def update(self, instance, validated_data):
        comments = validated_data.pop("comments")

        instance = super(ProductDetailSerializer, self).update(instance, validated_data)

        for comment_data in comments:
            if comment_data.get("id"):
                # comment has an ID so was pre-existing
                continue
            comment = Comment(**comment_data)
            comment.creator = self.context["request"].user
            comment.content_object = instance
            comment.save()

        return instance
