from django.urls import path

from . import views

app_name = "ui_preferences"

urlpatterns = [
    path(
        "default-column-preferences/",
        views.DefaultColumnPreferencesView.as_view(),
        name="default-column-preferences",
    )
]
