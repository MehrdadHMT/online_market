from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import (ProductSerializer, ProductDetailSerializer, CommentSerializer, ProductScoreSerializer,
                          CartItemSerializer, AddCartItemSerializer, RemoveCartItemSerializer)
from .permissions import IsAdminUserOrReadOnly, IsAdminUserOrObjectCreator
from .models import Product, CartItem, ShopOrder
from .validators import check_product_existence, check_product_quantity


class ProductView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class CommentView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrObjectCreator]
    serializer_class = CommentSerializer

    def get_queryset(self):
        p = Product.objects.get(pk=self.kwargs.get('pk'))
        comments = p.comments.all()
        if self.request.user.is_staff:
            return comments
        elif self.request.method in permissions.SAFE_METHODS:
            return comments.filter(status='v')


class ProductScoreView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductScoreSerializer
    queryset = Product.objects.all()


# class CartItemView(generics.CreateAPIView):
#     serializer_class = CartItemSerializer
#     queryset = CartItem


class CartItemView(APIView):
    def post(self, request):
        add_serializer = AddCartItemSerializer(data=request.data)
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
            elif not check_product_quantity(pid, quantity):
                data.append(
                    {"id": pid, "success": False,
                     "message": "There are not enough number of this product in the store!"}
                )
            else:
                data.append(
                    {"id": pid, "success": True, "message": "The product added to the cart, successfully"}
                )
                serializer = CartItemSerializer(data=item, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        serializer = RemoveCartItemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        items_id = serializer.validated_data['items_list']

        if items_id:
            CartItem.objects.filter(id__in=items_id, user=request.user).delete()
        else:
            CartItem.objects.filter(user=request.user).delete()

        return Response({"message": "Items are successfully deleted"}, status=status.HTTP_200_OK)


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
            data["time"] = time
        else:
            data["message"] = "There is no cart items!!!"

        return Response(data, status=status.HTTP_200_OK)


class TrackView(APIView):
    def get(self, request):
        user = request.user
        items = ShopOrder.objects.filter(user=user)

        if items:
            orders_list = list()
            for item in items:
                orders_list.append(
                    {
                        "id": item.id,
                        "track_id": item.track_id,
                        "status": item.status,
                        "created_at": item.created_at
                    }
                )

            return Response(orders_list, status=status.HTTP_200_OK)
        else:
            data = {"message": "You have no shopping order"}
            return Response(data, status=status.HTTP_200_OK)


class TrackDetailView(APIView):
    def get(self, request, pk):
        user = request.user

        try:
            item = ShopOrder.objects.get(user=user, pk=pk)

            data = {
                # "id": item.id,
                "track_id": item.track_id,
                "status": item.status,
                "created_at": item.created_at
            }
        except ShopOrder.DoesNotExist:
            data = {"message": "You don't have an order with the entered id!"}

        return Response(data, status=status.HTTP_200_OK)
