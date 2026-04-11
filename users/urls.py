from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "users/<uuid>/activate/<token>/",
        views.UserActivateView.as_view(),
        name="activate",
    ),
    path("token/", views.TokenObtainPairView().as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.TokenRefreshView().as_view(), name="token_refresh"),
]
