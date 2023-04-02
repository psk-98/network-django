from django.urls import include, path
from knox import views as knox_views

from .api import GetUserAPI, LoginAPI, RegisterAPI, UpdateProfileAPI, UserAPI, is_used

urlpatterns = [
    path("auth", include("knox.urls")),
    path("auth/register/", RegisterAPI.as_view()),
    path("auth/login/", LoginAPI.as_view()),
    path("auth/user", UserAPI.as_view()),
    path("auth/is_used", is_used),
    path("auth/profile", GetUserAPI.as_view()),
    path("auth/updateprofile", UpdateProfileAPI.as_view()),
    path("auth/logout", knox_views.LogoutAllView.as_view(), name="knox_logout"),
]
