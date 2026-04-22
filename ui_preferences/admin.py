from django.contrib import admin

from . import models


@admin.register(models.FilterVariant)
class FilterVariantAdmin(admin.ModelAdmin):
    list_display = ("uuid", "table_id", "name", "created_by")
    search_fields = ("uuid", "table_id", "name")
    list_filter = ("table_id", "is_public")


@admin.register(models.UserDefaultFilterVariant)
class UserDefaultFilterVariantAdmin(admin.ModelAdmin):
    list_display = ("user", "filter_variant")
    search_fields = ("user__username", "filter_variant__name")


@admin.register(models.FilterDefinition)
class FilterDefinitionAdmin(admin.ModelAdmin):
    list_display = ("table_id", "name", "label", "required", "is_visible_by_default")
    search_fields = ("name",)
    list_filter = ("table_id", "required", "is_visible_by_default")


@admin.register(models.UserFilterPreference)
class UserFilterPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "filter_definition", "is_visible")
    search_fields = ("user__username", "filter_definition__name")
    list_filter = ("user", "is_visible")


@admin.register(models.UserColumnPreference)
class UserColumnPreferenceAdmin(admin.ModelAdmin):
    list_diplay = (
        "user",
        "table_id",
        "key",
        "expression",
        "label",
        "is_visible",
        "order",
    )
    search_fields = ("user__username", "table_id", "key", "expression", "label")
    list_filter = ("is_visible",)
    ordering = ("user__username", "order")
