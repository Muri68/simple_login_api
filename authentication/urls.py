from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    # path('profile/', UserProfileView.as_view(), name='profile'),
]
