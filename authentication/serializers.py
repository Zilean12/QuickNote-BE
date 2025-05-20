from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .utils import register_social_user
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()

from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import serializers
from django.conf import settings

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token,
                requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            )

            # Debug print (remove in production)
            print("Token Validation Successful")
            print(f"Audience: {idinfo['aud']}")
            print(f"Client ID: {settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}")

            if idinfo['aud'] != settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:
                raise serializers.ValidationError(
                    f"Audience mismatch. Expected: {settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}, Got: {idinfo['aud']}"
                )

            return {
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'provider': 'google'
            }

        except ValueError as e:
            raise serializers.ValidationError(f"Token validation failed: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Unexpected error: {str(e)}")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'auth_provider'
        ]
        read_only_fields = ['id', 'auth_provider']

class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except Exception as e:
            raise serializers.ValidationError('Invalid or expired token')

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }