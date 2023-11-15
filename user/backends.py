from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class SpotifyAuthenticationBackend(BaseBackend):
    def authenticate(self, request, spotify_id=None):
        if spotify_id is None:
            return None
        try:
            return User.objects.get(username=spotify_id)
        except User.DoesNotExist:

            return None