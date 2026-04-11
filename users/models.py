from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(blank=False, unique=True)
    first_name = models.CharField(blank=True, max_length=128)
    last_name = models.CharField(blank=True, max_length=128)
    is_staff = models.BooleanField(
        default=False, help_text="The user can access the admin site"
    )
    is_active = models.BooleanField(
        default=False, help_text="The user account is active"
    )
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    def __str__(self):
        return f"User username={self.username} email={self.email}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
