from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
# from rest_framework.authtoken import views as rest_views

from . import views

urlpatterns = [
    path('products/', views.ProductView.as_view(), name='api_product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='api_product_detail'),
    path('opinion/<int:pk>/', views.CommentView.as_view(), name='api_comment')
]

urlpatterns = format_suffix_patterns(urlpatterns)

# urlpatterns += [
#     path("auth/", include("user_auth.urls")),
#     path("token-auth/", rest_views.obtain_auth_token, name='api-token-auth')
# ]
