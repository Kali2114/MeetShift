"""
Views for user app.
"""

import logging

from core.models import Conversation, Message, Notification, User, UserProfile
from core.tasks import send_activation_email_task
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
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
from user.forms import MessageForm, UserEditForm, UserProfileForm, UserRegisterForm
from user.services import create_notification
from user.utils import (
    attach_other_participant,
    build_activation_link,
    user_conversations_queryset,
)

logger = logging.getLogger(__name__)


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

        logger.info(
            "User registered and activation email queued: user_id=%s email=%s",
            self.object.id,
            self.object.email,
        )

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

    def form_valid(self, form):
        """Log profile update."""
        response = super().form_valid(form)

        logger.info(
            "User profile updated: user_id=%s",
            self.request.user.id,
        )

        return response

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

    def form_valid(self, form):
        """Log user account update."""
        response = super().form_valid(form)

        logger.info(
            "User account updated: user_id=%s email=%s",
            self.request.user.id,
            self.request.user.email,
        )

        return response

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

    def form_valid(self, form):
        """Log user account deletion."""
        logger.warning(
            "User account deleted: user_id=%s email=%s",
            self.request.user.id,
            self.request.user.email,
        )

        return super().form_valid(form)


class NotificationReadView(LoginRequiredMixin, View):
    """Mark notifications as read and redirect to their target."""

    def get(self, request, pk):
        """Get current user's notifications."""
        notification = get_object_or_404(Notification, pk=pk, user=self.request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read"])

        logger.info(
            "Notification marked as read: notification_id=%s user_id=%s "
            "meeting_id=%s conversation_id=%s",
            notification.id,
            request.user.id,
            notification.meeting_id,
            notification.conversation_id,
        )

        if notification.conversation_id:
            return redirect("user:conversation-detail", pk=notification.conversation_id)

        return redirect("meeting:detail-meeting", pk=notification.meeting_id)


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

            logger.info(
                "User account activated: user_id=%s email=%s",
                user.id,
                user.email,
            )
            messages.success(
                request, "Your account has been activated. You can now log in."
            )
        else:
            messages.error(request, "Activation link is invalid.")
            logger.warning(
                "Invalid activation link used: uidb64=%s",
                uidb64,
            )

        return redirect("login")


class ConversationListView(LoginRequiredMixin, ListView):
    """Display current user's conversations."""

    model = Conversation
    template_name = "user/conversation_list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        """Return current user's conversations, newest activity first."""
        return user_conversations_queryset(self.request.user)

    def get_context_data(self, **kwargs):
        """Attach the other participant to each conversation for display."""
        context = super().get_context_data(**kwargs)
        context["conversations"] = attach_other_participant(
            context["conversations"], self.request.user
        )

        return context


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """Display a conversation thread and mark incoming messages as read."""

    model = Conversation
    template_name = "user/conversation_detail.html"
    context_object_name = "conversation"

    def get_queryset(self):
        """Return conversations the current user is part of."""
        return Conversation.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        )

    def get(self, request, *args, **kwargs):
        """Render the thread and mark the other participant's messages as read."""
        self.object = self.get_object()
        self.object.messages.filter(is_read=False).exclude(sender=request.user).update(
            is_read=True
        )

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Attach the other participant, message form, and sidebar conversations."""
        context = super().get_context_data(**kwargs)
        context["other_user"] = self.object.other_participant(self.request.user)
        context["message_form"] = MessageForm()
        context["conversations"] = attach_other_participant(
            user_conversations_queryset(self.request.user), self.request.user
        )
        context["active_conversation_id"] = self.object.id

        return context


class SendMessageView(LoginRequiredMixin, View):
    """Send a message in a conversation."""

    def post(self, request, pk):
        """Create the message if valid and redirect back to the thread."""
        conversation = get_object_or_404(
            Conversation.objects.filter(Q(user1=request.user) | Q(user2=request.user)),
            pk=pk,
        )
        form = MessageForm(request.POST)

        if form.is_valid():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=form.cleaned_data["content"],
            )

            recipient = conversation.other_participant(request.user)
            create_notification(
                user=recipient,
                conversation=conversation,
                message=f"New message from {request.user.name}",
            )

            logger.info(
                "Message sent: conversation_id=%s sender_id=%s",
                conversation.id,
                request.user.id,
            )
        else:
            messages.error(request, "Message cannot be empty.")

        return redirect("user:conversation-detail", pk=conversation.id)


class StartConversationView(LoginRequiredMixin, View):
    """Start or resume a conversation with another user."""

    def get(self, request, user_id):
        """Find or create the conversation and redirect to its thread."""
        if user_id == request.user.id:
            messages.error(request, "You cannot start a conversation with yourself.")
            return redirect("user:conversation-list")

        other_user = get_object_or_404(User, pk=user_id)
        conversation, _ = Conversation.objects.get_or_create_between(
            request.user, other_user
        )

        return redirect("user:conversation-detail", pk=conversation.id)


class NewMessageView(LoginRequiredMixin, ListView):
    """List users to start a new conversation with."""

    model = User
    template_name = "user/new_message.html"
    context_object_name = "users"

    def get_queryset(self):
        """Return all users except the current one."""
        return User.objects.exclude(id=self.request.user.id).order_by("name")
