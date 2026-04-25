import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager
from .tokens import account_activation_token_generator


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(blank=False, unique=True)
    first_name = models.CharField(blank=True, max_length=128)
    last_name = models.CharField(blank=True, max_length=128)
    is_staff = models.BooleanField(default=False, help_text="The user can access the admin site")
    is_active = models.BooleanField(default=False, help_text="The user account is active")
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    class Meta:
        ordering = ["username"]
        permissions = [
            ("manage_user_groups", "Can manage the groups of a user"),
            ("manage_group_permissions", "Can manage the permissions of a group"),
        ]

    def __str__(self):
        return f"User username={self.username} email={self.email}"

    def save(self, *args, **kwargs):
        if not self.password:
            self.set_unusable_password()
        self.full_clean()
        super().save(*args, **kwargs)

    def get_activation_token(self):
        return account_activation_token_generator.make_token(self)

    def get_activation_link(self):
        return f"{settings.FRONTEND_URL}/users/{self.uuid}/activate/{self.get_activation_token()}"

    def activate(self, token):
        if account_activation_token_generator.check_token(self, token):
            self.is_active = True
            self.save()
            return True
        else:
            return False


class UserPreferences(models.Model):
    class DateFormatChoices(models.TextChoices):
        ISO = "is", "YYYY-MM-DD"
        EU_DOT = "ed", "DD.MM.YYYY"
        EU_SLASH = "es", "DD/MM/YYYY"
        US = "us", "MM/DD/YYYY"
        DOT = "dt", "YYYY.MM.DD"
        CMP = "cp", "YYYYMMDD"

    class DecimalFormatChoices(models.TextChoices):
        US = "us", "1,234,567.8"
        EU = "eu", "1 234 567,8"
        DE = "de", "1.234.567,8"
        NONE = "nn", "1234567.8"
        CH = "ch", "1'234'567.8"

    class TimeFormatChoices(models.TextChoices):
        H12 = "12", "12-hour"
        H24 = "24", "24-hour"

    class FioriThemeChoices(models.TextChoices):
        SAP_HORIZON = "sap_horizon", "Morning Horizon (Light)"
        SAP_HORIZON_DARK = "sap_horizon_dark", "Evening Horizon (Dark)"
        SAP_HORIZON_HCB = "sap_horizon_hcb", "Horizon High Contrast Black"
        SAP_HORIZON_HCW = "sap_horizon_hcw", "Horizon High Contrast White"
        SAP_HORIZON_AUTO = "sap_horizon_auto", "OS Adaptive Horizon Theme"
        SAP_HORIZON_HC_AUTO = ("sap_horizon_hc_auto", "OS Adaptive Hight Contrast Horizon Theme")
        SAP_FIORI_3 = "sap_fiori_3", "Quartz Light"
        SAP_FIORI_3_DARK = "sap_fiori_3_dark", "Quartz Dark"
        SAP_FIORI_3_HCB = "sap_fiori_3_hcb", "Quartz High Contrast Black"
        SAP_FIORI_3_HCW = "sap_fiori_3_hcw", "Quartz High Contrast White"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_format = models.CharField(max_length=2, choices=DateFormatChoices, default=DateFormatChoices.ISO)
    decimal_format = models.CharField(max_length=2, choices=DecimalFormatChoices, default=DecimalFormatChoices.US)
    time_zone = models.CharField(max_length=64, default="Etc/UTC")
    time_format = models.CharField(max_length=2, choices=TimeFormatChoices, default="24")
    fiori_theme = models.CharField(max_length=19, choices=FioriThemeChoices, default=FioriThemeChoices.SAP_HORIZON_AUTO)
    show_timezone = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User Preferences"
        verbose_name_plural = "User Preferences"

    def __str__(self):
        return f"Preferences for {self.user}"
