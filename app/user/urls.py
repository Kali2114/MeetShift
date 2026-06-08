"""
URLs for user app.
"""

from django.contrib.auth.views import PasswordChangeView
from django.urls import path
from user import views

app_name = "user"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("profile/edit", views.UserProfileUpdateView.as_view(), name="profile-edit"),
    path(
        "profile/<int:pk>/",
        views.UserProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "account/settings/",
        views.AccountSettingsView.as_view(),
        name="account-settings",
    ),
    path(
        "account/edit",
        views.UserUpdateView.as_view(),
        name="user-edit",
    ),
    path(
        "account/password-change/",
        PasswordChangeView.as_view(template_name="user/password_change.html"),
        name="password-change",
    ),
    path(
        "account/delete/",
        views.UserDeleteView.as_view(),
        name="user-delete",
    ),
]
