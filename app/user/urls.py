"""
URLs for user app.
"""

from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy
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
    path(
        "account/password-reset/",
        PasswordResetView.as_view(
            template_name="user/password_reset.html",
            email_template_name="user/password_reset_email.html",
            subject_template_name="user/password_reset_subject.txt",
            success_url=reverse_lazy("user:password-reset-done"),
        ),
        name="password-reset",
    ),
    path(
        "account/password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="user/password_reset_done.html",
        ),
        name="password-reset-done",
    ),
    path(
        "account/password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="user/password_reset_confirm.html",
            success_url=reverse_lazy("user:password-reset-complete"),
        ),
        name="password-reset-confirm",
    ),
    path(
        "account/password-reset-complete/",
        PasswordResetCompleteView.as_view(
            template_name="user/password_reset_complete.html",
        ),
        name="password-reset-complete",
    ),
]
