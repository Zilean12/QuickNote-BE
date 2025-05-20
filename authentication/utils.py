from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
User = get_user_model()

def register_social_user(provider, email, name):
    try:
        user = User.objects.get(email=email)
        if user.auth_provider != provider:
            raise Exception(
                f"Account exists with {user.auth_provider} authentication"
            )
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            username=email,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if name else '',
            password=User.objects.make_random_password(),
            auth_provider=provider
        )
    
    refresh = RefreshToken.for_user(user)
    return {
        'email': user.email,
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }