from rest_framework import serializers
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404

from user_auth.serializers import UserSerializer
from .models import Product, Comment, CartItem, ShopOrder


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["user", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("There is no product with the entered id")

        return value

    def create(self, validated_data):
        product = Product.objects.get(pk=validated_data['id'])
        user = self.context['request'].user
        return product.comments.create(content=validated_data['content'], user=user)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['type', 'brand', 'name']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['id', 'vote_quantity', 'product_quantity']
        read_only = ['created_at', 'modified_at']


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


class CartItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(validators=[MinValueValidator(1)], required=True)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)], required=True)

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

    def validate(self, data):
        if self.context:
            if self.context['request'].method == 'POST':    # for AddCartItemSerializer's nested serializer!
                return data
        try:
            p = Product.objects.get(pk=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("There is no product with the entered id")

        if p.product_quantity < data['quantity']:
            raise serializers.ValidationError("There are not enough number of this product in the store!")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        product = get_object_or_404(Product, pk=validated_data['product_id'])
        quantity = validated_data['quantity']
        return CartItem.objects.create(user=user, product=product, quantity=quantity)


class CartItemListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class CartItemEditSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

    def validate(self, data):
        p = Product.objects.get(pk=self.instance.product_id)
        if p.product_quantity < data['quantity']:
            raise serializers.ValidationError("There are not enough number of this product in the store!")

        return data


class AddCartItemSerializer(serializers.Serializer):
    items_list = serializers.ListField(child=CartItemCreateSerializer(), required=True, allow_empty=False)


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


class ShopOrderSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = ShopOrder
        exclude = ['user', 'status']


class ShopOrderDetailSerializer(ShopOrderSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ShopOrder
        exclude = ['user']
