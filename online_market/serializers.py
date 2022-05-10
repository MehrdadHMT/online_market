from rest_framework import serializers
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework.fields import CurrentUserDefault

from user_auth.serializers import UserSerializer
from .models import Product, Comment, CartItem


# class VerifiedCommentsSerializer(serializers.ListSerializer):
#     def to_representation(self, data):
#         data = data.filter(status='v')
#         return super(VerifiedCommentsSerializer, self).to_representation(data)


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "creator", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]

    def create(self, validated_data):
        product_id = self.context['request'].data.get('product_id')
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
        else:
            raise TypeError("'product_id' must be passed (as an integer)!")

        user = self.context['request'].user
        return product.comments.create(**validated_data, creator=user)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['type', 'brand', 'name']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['vote_quantity', 'product_quantity']
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


class ProductScoreSerializer(serializers.ModelSerializer):
    score = serializers.DecimalField(decimal_places=2, max_digits=3, required=True,
                                     validators=[MinValueValidator(-5), MaxValueValidator(5)])

    class Meta:
        model = Product
        fields = ['score']

    def update(self, instance, validated_data):
        instance.vote_quantity += 1
        instance.score = (
                ((instance.score * (instance.vote_quantity - 1)) + validated_data.get('score')) / instance.vote_quantity
        )
        instance.save()

        return instance


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(validators=[MinValueValidator(1)])
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

    def create(self, validated_data):
        user = self.context['request'].user
        product = get_object_or_404(Product, pk=validated_data['product_id'])
        quantity = validated_data['quantity']
        return CartItem.objects.create(user=user, product=product, quantity=quantity)

    # def validate(self, data):
    #     try:
    #         product = Product.objects.get(pk=data['product_id'])
    #     except Product.DoesNotExist:
    #         raise serializers.ValidationError('There is no product with the entered id!')
    #     if product.product_quantity < data['quantity']:
    #         raise serializers.ValidationError('There is not enough number of this product in the store!')
    #     return data


class AddCartItemSerializer(serializers.Serializer):
    items_list = serializers.ListField(child=CartItemSerializer(), required=True, allow_empty=False)


class RemoveCartItemSerializer(serializers.Serializer):
    items_list = serializers.ListField(child=serializers.IntegerField(validators=[MinValueValidator(1)]),
                                       required=True, allow_empty=True)
    delete_all = serializers.BooleanField(required=False)

    def validate(self, data):
        user = self.context['request'].user

        if not data['items_list']:
            if 'delete_all' not in data.keys():
                raise serializers.ValidationError("One of the 'items_list' or 'delete_all' fields must be prepared")
            if not data['delete_all']:
                raise serializers.ValidationError("You should set 'delete_all' option to 'True' or enter some items id")

        if data['items_list'] and 'delete_all' in data.keys():
            if data['delete_all']:
                raise serializers.ValidationError("Don't use 'items_list' and 'delete_all' options together!")

        for item_id in data['items_list']:
            try:
                CartItem.objects.get(pk=item_id, user=user)
            except CartItem.DoesNotExist:
                raise serializers.ValidationError(f'There is no cart item with id={item_id}!')

        return data
