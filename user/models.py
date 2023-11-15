import datetime

import requests
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from requests import RequestException

from beat_notify.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


class User(AbstractUser):
    location = models.CharField(max_length=100, blank=True)
    spotify_access_token = models.CharField(max_length=255, blank=True, null=True)
    spotify_refresh_token = models.CharField(max_length=255, blank=True, null=True)
    spotify_token_expires = models.DateTimeField(null=True, blank=True)

    def set_spotify_tokens(self, access_token, refresh_token, expires_in):
        self.spotify_access_token = access_token
        self.spotify_refresh_token = refresh_token
        self.spotify_token_expires = timezone.now() + datetime.timedelta(seconds=expires_in)
        self.save()

    def refresh_spotify_token(self):
        try:
            refresh_token_url = 'https://accounts.spotify.com/api/token'
            response = requests.post(refresh_token_url, data={
                'grant_type': 'refresh_token',
                'refresh_token': self.spotify_refresh_token,
                'client_id': SPOTIFY_CLIENT_ID,
                'client_secret': SPOTIFY_CLIENT_SECRET,
            })
            response.raise_for_status()

            res_data = response.json()
            if 'access_token' in res_data:
                expires_in = res_data.get('expires_in', 3600)
                self.set_spotify_tokens(
                    access_token=res_data['access_token'],
                    refresh_token=self.spotify_refresh_token,
                    expires_in=expires_in
                )
        except RequestException as e:
            print(f'Failed to refresh Spotify token: {e}')

    def __str__(self):
        return self.username
