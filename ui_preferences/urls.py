from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = "ui_preferences"


router = SimpleRouter()
router.register(
    r"filter-definitions", views.FilterDefinitionsViewSet, basename="filter-definitions"
)
router.register(
    r"user-column-preferences",
    views.UserColumnPreferencesViewSet,
    basename="user-column-preferences",
)
router.register(
    r"filter-variants", views.FilterVariantsViewSet, basename="filter-variants"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "default-column-preferences/",
        views.DefaultColumnPreferencesView.as_view(),
        name="default-column-preferences",
    ),
    path(
        "user-filter-preferences/",
        views.UserFilterPreferencesUpdateView.as_view(),
        name="update-user-filter-preferences",
    ),
]
