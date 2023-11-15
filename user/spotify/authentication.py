import logging
from datetime import timedelta

from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

from beat_notify.settings import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI, SPOTIFY_CLIENT_SECRET


class SpotifyAuthRedirect(APIView):
    def get(self, request, *args, **kwargs):
        print(SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI)
        scope = "user-library-read"
        auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={SPOTIFY_CLIENT_ID}&scope={scope}&redirect_uri={SPOTIFY_REDIRECT_URI}"
        return redirect(auth_url)


logger = logging.getLogger(__name__)


class SpotifyCallback(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        auth_token_url = 'https://accounts.spotify.com/api/token'

        try:
            res = requests.post(auth_token_url, data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': SPOTIFY_REDIRECT_URI,
                'client_id': SPOTIFY_CLIENT_ID,
                'client_secret': SPOTIFY_CLIENT_SECRET
            })
            res.raise_for_status()
            res_data = res.json()
            access_token = res_data.get('access_token')
            refresh_token = res_data.get('refresh_token')
            expires_in = res_data.get('expires_in')
        except requests.exceptions.RequestException as e:
            logger.error(f'Spotify token retrieval failed: {e}')
            logger.error(f'Response content: {res.content if res else "No response"}')
            return Response({'error': 'Failed to retrieve tokens from Spotify.'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile_url = 'https://api.spotify.com/v1/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(user_profile_url, headers=headers)

        if profile_response.status_code != 200:

            return Response({'error': 'Could not fetch user profile from Spotify.'},
                            status=profile_response.status_code)

        profile_data = profile_response.json()
        spotify_id = profile_data.get('id')

        user = get_or_create_user(spotify_id, access_token, refresh_token, expires_in)

        user = authenticate(spotify_id=spotify_id)
        if user:
            login(request, user)
            return Response({'success': 'User authenticated.'})
        else:
            return Response({'error': 'Authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)



def get_or_create_user(spotify_id, access_token, refresh_token, expires_in):
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=spotify_id,
        defaults={
            'location': '',
            'spotify_access_token': access_token,
            'spotify_refresh_token': refresh_token,
            'spotify_token_expires': timezone.now() + timedelta(seconds=expires_in),
        }
    )

    if not created:
        user.set_spotify_tokens(access_token, refresh_token, expires_in)

    return user