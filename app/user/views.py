from core.models import Notification, User, UserProfile
from core.tasks import send_activation_email_task
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
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
from user.utils import build_activation_link


class RegisterView(CreateView):
    """Register new user."""

    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        """Create inactive user and send activation email."""
        response = super().form_valid(form)
        activation_link = build_activation_link(self.request, self.object)
        send_activation_email_task.delay(self.object.email, activation_link)

        messages.success(
            self.request,
            "Account created. Check your email to activate your account.",
        )

        return response


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


class ActivateAccountView(View):
    """Activate user account for email link."""

    def get(self, request, uidb64, token):
        """Activate user if token is valid."""
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])

        return redirect("login")
