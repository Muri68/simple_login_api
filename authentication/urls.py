from django.urls import path
from .views import (
    UsernameCheckView, CodeVerificationView, UserListView
)

urlpatterns = [
    path('check-username/', UsernameCheckView.as_view(), name='check-username'),
    path('verify-code/', CodeVerificationView.as_view(), name='verify-code'),
    path('users/', UserListView.as_view(), name='user-list'),
    # path('register/', UserRegistrationView.as_view(), name='register'),
    # path('profile/', UserProfileView.as_view(), name='profile'),
]
