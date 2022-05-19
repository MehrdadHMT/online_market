from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
	path('products/', views.ProductView.as_view(), name='api_product'),
	path('products/<int:pk>/', views.ProductDetailView.as_view(), name='api_product_detail'),
	path('opinion/', views.CommentCreateView.as_view(), name='api_comment_create'),
	path('opinion/<int:pk>/', views.CommentListView.as_view(), name='api_comment_list'),
	path('opinion/edit/<int:pk>/', views.CommentEditView.as_view(), name='api_comment_list'),
	path('score/<int:pk>/', views.ProductScoreView.as_view(), name='api_score'),
	path('cart/add/', views.CartItemView.as_view(), name='api_cart_add_item'),
	path('cart/remove/', views.CartItemView.as_view(), name='api_cart_remove_item'),
	path('cart/', views.CartItemListView.as_view(), name='api_cart_list_items'),
	path('cart/<int:pk>/', views.CartItemEditView.as_view(), name='api_edit_cart_items'),
	path('shop/', views.ShopView.as_view(), name='api_shop'),
	path('track/', views.TrackShopOrderView.as_view(), name='api_orders'),
	path('track/<int:pk>/', views.ShopOrderDetailView.as_view(), name='api_order_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
