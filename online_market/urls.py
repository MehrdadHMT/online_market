from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('product/', views.ProductListView.as_view(), name='api_product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='api_product_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
