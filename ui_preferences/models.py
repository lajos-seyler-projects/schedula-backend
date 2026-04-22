import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from users.models import User


class FilterVariant(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=120, blank=True, null=True)
    filters = models.JSONField(blank=True, null=True)
    exclude_filters = models.JSONField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    execute_on_selection = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        related_name="filter_variants",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Filter Variant"
        verbose_name_plural = "Filter Variants"
        constraints = [
            models.UniqueConstraint(
                fields=["table_id", "name", "created_by"],
                name="unique_variant_per_user",
            ),
            models.UniqueConstraint(
                fields=["table_id", "slug", "created_by"],
                name="unique_slug_per_user",
            ),
        ]

    def __str__(self):
        return f"Filter Variant - {self.name} ({self.table_id}, user={self.created_by})"

    def save(self, *args, **kwargs):
        existing = FilterVariant.objects.filter(
            table_id=self.table_id, created_by=self.created_by
        )
        if self.pk:
            existing = existing.exclude(pk=self.pk)

        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1

        while existing.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug
        return super().save(*args, **kwargs)


class UserDefaultFilterVariant(models.Model):
    user = models.ForeignKey(
        User, related_name="default_filter_variants", on_delete=models.CASCADE
    )
    filter_variant = models.ForeignKey(
        FilterVariant, related_name="default_variants", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "User Default Filter Variant"
        verbose_name_plural = "User Default Filter Variants"

    def clean(self):
        super().clean()
        existing = UserDefaultFilterVariant.objects.filter(
            user=self.user, filter_variant__table_id=self.filter_variant.table_id
        )
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError(
                f"User {self.user} already have a default filter variant for table {self.filter_variant.table_id}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class FilterDefinition(models.Model):
    table_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    query_parameter = models.CharField(max_length=100)
    required = models.BooleanField(default=False)
    is_visible_by_default = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Filter Definition"
        verbose_name_plural = "Filter Definitions"
        constraints = [
            models.UniqueConstraint(
                fields=["table_id", "name"], name="unique_table_filter_definition"
            )
        ]

    def __str__(self):
        return f"{self.table_id} - {self.name}"


class UserFilterPreference(models.Model):
    user = models.ForeignKey(
        User, related_name="filter_preferences", on_delete=models.CASCADE
    )
    filter_definition = models.ForeignKey(
        FilterDefinition, related_name="user_preferences", on_delete=models.CASCADE
    )
    is_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User Filter Preferences"
        verbose_name_plural = "User Filter Preferences"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "filter_definition"],
                name="unique_user_filter_definition_preference",
            )
        ]

    def __str__(self):
        return f"{self.filter_definition.table_id} - {self.filter_definition.name} (user={self.user.username})"


class UserColumnPreference(models.Model):
    user = models.ForeignKey(
        User, related_name="column_preferences", on_delete=models.CASCADE
    )
    table_id = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    expression = models.JSONField(default=dict)
    label = models.CharField(max_length=100)
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

    class Meta:
        verbose_name = "User Column Preferences"
        verbose_name_plural = "User Column Preferences"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "table_id", "key"],
                name="unique_user_table_column_preference",
            )
        ]
        ordering = ["user", "table_id", "order"]

    def __str__(self):
        return f"{self.table_id} - {self.key} (user={self.user.username})"
