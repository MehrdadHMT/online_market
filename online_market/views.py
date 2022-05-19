from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers
from .permissions import IsAdminUserOrReadOnly, IsAdminUserOrObjectCreator, IsObjectOwner
from .models import Product, Comment, CartItem, ShopOrder
from .validators import check_product_existence, check_item_existence, check_product_quantity


class ProductView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = serializers.ProductDetailSerializer


class ProductScoreView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.ProductScoreSerializer
    queryset = Product.objects.all()


class CommentListView(generics.ListAPIView):
    permission_classes = [IsAdminUserOrObjectCreator]
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        p = Product.objects.get(pk=self.kwargs.get('pk'))
        comments = p.comments.all()
        if self.request.user.is_staff:
            return comments
        elif self.request.method in permissions.SAFE_METHODS:
            return comments.filter(status='v')


class CommentCreateView(APIView):
    permission_classes = [IsAdminUserOrObjectCreator]

    def post(self, request):
        serializer = serializers.CommentCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsObjectOwner]
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()


class CartItemView(APIView):
    def post(self, request):
        add_serializer = serializers.AddCartItemSerializer(data=request.data, context={'request': request})
        add_serializer.is_valid(raise_exception=True)

        data = list()
        items_list = list(map(lambda x: dict(x), add_serializer.validated_data['items_list']))
        for item in items_list:
            pid = item['product_id']
            quantity = item['quantity']
            if not check_product_existence(pid):
                data.append(
                    {"id": pid, "success": False, "message": "There is no product with the entered id!"}
                )
            elif check_item_existence(pid):
                tmp_item = CartItem.objects.get(product_id=pid)
                product = Product.objects.get(pk=pid)
                if tmp_item.quantity + quantity > product.product_quantity:
                    data.append(
                        {"id": pid, "success": False, "message": f"There is an item with product_id={pid} and "
                                                                 f"the total quantity is more than available items"
                                                                 f" in the store!"}
                    )
                else:
                    tmp_item.quantity += quantity
                    tmp_item.save()
                    data.append(
                        {"id": pid, "success": True, "message": f"There is an item with product_id={pid} and "
                                                                f"the quantity is updated"}
                    )
            elif not check_product_quantity(pid, quantity):
                data.append(
                    {"id": pid, "success": False,
                     "message": "There are not enough number of this product in the store!"}
                )
            else:
                serializer = serializers.CartItemCreateSerializer(data=item, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                data.append(
                    {"id": pid, "success": True, "message": "The product added to the cart, successfully"}
                )

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        serializer = serializers.RemoveCartItemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        items_id = serializer.validated_data['items_list']

        if items_id:
            CartItem.objects.filter(id__in=items_id, user=request.user).delete()
        else:
            CartItem.objects.filter(user=request.user).delete()

        return Response({"message": "Items are successfully deleted"}, status=status.HTTP_200_OK)


class CartItemListView(generics.ListAPIView):
    serializer_class = serializers.CartItemListSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class CartItemEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsObjectOwner]
    serializer_class = serializers.CartItemEditSerializer
    queryset = CartItem.objects.all()


class ShopView(APIView):
    def get(self, request):
        user = request.user
        track_id = ShopOrder.generate_track_id()
        data = dict()

        items = CartItem.objects.filter(user=user)
        if items:
            order = ShopOrder.objects.create(user=user, track_id=track_id)
            items.delete()

            date, time = str(order.created_at).split(' ')
            data["track_id"] = track_id
            data["date"] = date
            data["time"] = time.split('.')[0]
        else:
            data["message"] = "There is no cart items!!!"

        return Response(data, status=status.HTTP_200_OK)


class TrackShopOrderView(generics.ListAPIView):
    serializer_class = serializers.ShopOrderSerializer

    def get_queryset(self):
        return ShopOrder.objects.filter(user=self.request.user)


class ShopOrderDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.ShopOrderDetailSerializer

    def get_queryset(self):
        return ShopOrder.objects.filter(user=self.request.user)
