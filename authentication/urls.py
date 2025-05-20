from django.urls import path
from .views import (
    GoogleSocialAuthView,
    LogoutView,
    UserDetailView
)

app_name = 'authentication'

urlpatterns = [
    path('google/', GoogleSocialAuthView.as_view(), name='google-auth'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
]