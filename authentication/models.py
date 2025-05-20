
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    auth_provider = models.CharField(max_length=50, default='email')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email