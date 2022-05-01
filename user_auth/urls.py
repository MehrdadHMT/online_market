from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='api_user_register'),
    path('login/', views.LoginView.as_view(), name='api_user_login'),
    path('logout/', views.LogoutView.as_view(), name='api_user_logout'),
    path('get-profile/', views.ProfileView.as_view(), name='api_get_profile'),
    path('set-profile/', views.ProfileView.as_view(), name='api_set_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='api_change_password'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
