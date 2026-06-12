from core.models import Notification, UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from user.forms import UserEditForm, UserProfileForm, UserRegisterForm


class RegisterView(CreateView):
    """Register new user."""

    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class UserProfileView(LoginRequiredMixin, DetailView):
    """User profile view."""

    model = UserProfile
    template_name = "user/user_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """Return current user profile."""
        return self.request.user.user_profile


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update current profile user profile view."""

    form_class = UserProfileForm
    template_name = "user/user_edit_profile.html"
    success_url = reverse_lazy("user:profile")

    def get_object(self, queryset=None):
        """Return current user profile."""
        return self.request.user.user_profile


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """Display selected user's profile."""

    model = UserProfile
    template_name = "user/user_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """Return selected user's profile."""
        return get_object_or_404(UserProfile, user_id=self.kwargs["pk"])


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """Display account settings page."""

    template_name = "user/account_settings.html"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Update current user account."""

    form_class = UserEditForm
    template_name = "user/user_edit.html"
    success_url = reverse_lazy("user:account-settings")

    def get_object(self, queryset=None):
        """Return current user."""
        return self.request.user


class UserDeleteView(LoginRequiredMixin, DeleteView):
    """Delete current user account."""

    template_name = "user/user_delete.html"
    success_url = reverse_lazy("login")

    def get_object(self, queryset=None):
        """Return current user."""
        return self.request.user


class NotificationReadView(LoginRequiredMixin, View):
    """Mark notifications as read and redirect to meeting details."""

    def get(self, request, pk):
        """Get current user's notifications."""
        notification = get_object_or_404(Notification, pk=pk, user=self.request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return redirect("meeting:detail-meeting", pk=notification.meeting.id)


class NotificationListView(LoginRequiredMixin, ListView):
    """Display current user notifications list."""

    model = Notification
    template_name = "user/notification_list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        """Return current user's notifications."""
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
