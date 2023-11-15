from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'location', 'spotify_access_token', 'spotify_refresh_token', 'spotify_token_expires']
        read_only_fields = ['id', 'spotify_access_token', 'spotify_refresh_token', 'spotify_token_expires']