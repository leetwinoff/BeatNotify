from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .spotify.authentication import SpotifyAuthRedirect, SpotifyCallback
from .views import UserViewSet

router = DefaultRouter()

router.register("users", UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('spotify-auth-redirect/', SpotifyAuthRedirect.as_view(), name='spotify-auth-redirect'),
    path('callback/', SpotifyCallback.as_view(), name='spotify-callback'),
]