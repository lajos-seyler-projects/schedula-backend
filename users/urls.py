from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from . import views

app_name = "users"

router = DefaultRouter()
router.register(r"groups", views.GroupsViewSet, basename="groups")
router.register(r"permissions", views.PermissionsViewSet, basename="permissions")
router.register(r"users", views.UsersViewSet, basename="users")
router.register(
    r"users/(?P<uuid>[^/.]+)/groups",
    views.UserGroupsViewSet,
    basename="user_groups",
)
router.register(r"me", views.UserPreferencesViewSet, basename="me")

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "users/<uuid>/activate/<token>/",
        views.UserActivateView.as_view(),
        name="activate",
    ),
    path("token/", views.TokenObtainPairView().as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.TokenRefreshView().as_view(), name="token_refresh"),
    path(
        "token/blacklist/",
        views.TokenBlacklistView.as_view(),
        name="token_blacklist",
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "me/",
        views.CurrentUserRetrieveUpdateViewSet.as_view(
            {"patch": "update", "get": "retrieve"}
        ),
        name="me",
    ),
    path(
        "user-preferences/date-format-choices",
        views.DateFormatChoicesAPIView.as_view(),
        name="date-format-choices",
    ),
    path(
        "user-preferences/decimal-format-choices",
        views.DecimalFormatChoicesAPIView.as_view(),
        name="decimal-format-choices",
    ),
    path(
        "user-preferences/timezone-choices",
        views.TimezoneChoicesAPIView.as_view(),
        name="timezone-choices",
    ),
    path(
        "user-preferences/time-format-choices",
        views.TimeFormatChoicesAPIView.as_view(),
        name="time-format-choices",
    ),
    path(
        "user-preferences/fiori-theme-choices",
        views.FioriThemeChoicesAPIView.as_view(),
        name="fiori-theme-choices",
    ),
    path("", include(router.urls)),
]
