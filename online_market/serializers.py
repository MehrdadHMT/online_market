from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import serializers

from user_auth.serializers import UserSerializer
from .models import Product, Comment


class VerifiedCommentsSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(status='v')
        return super(VerifiedCommentsSerializer, self).to_representation(data)


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        # list_serializer_class = VerifiedCommentsSerializer
        fields = ["id", "creator", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]

    def create(self, validated_data):
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        user = self.context['request'].user
        return product.comments.create(**validated_data, creator=user)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['type', 'brand', 'name']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only = ['created_at', 'modified_at']
    # comments = CommentSerializer(many=True)
    #
    # def update(self, instance, validated_data):
    #     comments = validated_data.pop("comments")
    #
    #     instance = super(ProductDetailSerializer, self).update(instance, validated_data)
    #
    #     for comment_data in comments:
    #         if comment_data.get("id"):
    #             # comment has an ID so was pre-existing
    #             continue
    #         comment = Comment(**comment_data)
    #         comment.creator = self.context["request"].user
    #         comment.content_object = instance
    #         comment.save()
    #
    #     return instance
