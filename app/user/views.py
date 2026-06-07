from core.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from user.forms import UserProfileForm, UserRegisterForm


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
