from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
# from rest_framework.authtoken import views as rest_views

from . import views

urlpatterns = [
    path('products/', views.ProductView.as_view(), name='api_product'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='api_product_detail'),
    path('opinion/<int:pk>/', views.CommentView.as_view(), name='api_comment_list'),
    path('score/<int:pk>/', views.ProductScoreView.as_view(), name='api_score'),
    path('cart/add/', views.CartItemView.as_view(), name='api_cart_add_item'),
    path('cart/remove/', views.CartItemView.as_view(), name='api_cart_remove_item'),
    path('shop/', views.ShopView.as_view(), name='api_shop'),
    path('track/', views.TrackView.as_view(), name='api_orders'),
    path('track/<int:pk>/', views.TrackDetailView.as_view(), name='api_order_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

# urlpatterns += [
#     path("auth/", include("user_auth.urls")),
#     path("token-auth/", rest_views.obtain_auth_token, name='api-token-auth')
# ]
