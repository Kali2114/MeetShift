"""
URLs for user app.
"""

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
]
