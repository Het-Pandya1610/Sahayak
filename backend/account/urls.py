# account/urls.py
from django.urls import path
from .views import register_view, login_view, google_login_callback, get_user_profile, update_profile_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("google-login/", google_login_callback, name="google_login"),
    path("profile/", get_user_profile, name="profile"),
    path("profile/update/", update_profile_view, name="update_profile"),
]