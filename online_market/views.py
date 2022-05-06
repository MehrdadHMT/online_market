from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework import status, generics, permissions
from rest_framework.response import Response

from .serializers import ProductSerializer, ProductDetailSerializer, CommentSerializer
from .permissions import IsAdminUserOrReadOnly
from .models import Product, Comment


class ProductView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer

    # def get_serializer_class(self):
    #     if not self.request.user.is_authenticated:
    #         return ProductSerializer
    #     return ProductDetailSerializer


class CommentView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        p = Product.objects.get(pk=self.kwargs.get('pk'))
        # comments = Comment.objects.filter(comments=p)
        comments = p.comments.all()
        if self.request.user.is_staff:
            return comments
        elif self.request.method in permissions.SAFE_METHODS:
            return comments.filter(status='v')
