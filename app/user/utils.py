"""
Utils for user app.
"""

from core.models import Conversation
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Count, Max, Q
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def build_activation_link(request, user):
    """Build an activation link for the selected user."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_path = reverse(
        "user:activate-account",
        kwargs={
            "uidb64": uidb64,
            "token": token,
        },
    )

    return request.build_absolute_uri(activation_path)


def get_activate_account_url(uidb64, token):
    """Return activate account url."""
    return reverse(
        "user:activate-account",
        kwargs={
            "uidb64": uidb64,
            "token": token,
        },
    )


def user_conversations_queryset(user):
    """Return user's conversations, annotated with unread count, newest first."""
    return (
        Conversation.objects.filter(Q(user1=user) | Q(user2=user))
        .annotate(
            last_activity=Coalesce(Max("messages__created_at"), "created_at"),
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user),
            ),
        )
        .select_related("user1__user_profile", "user2__user_profile")
        .order_by("-last_activity")
    )


def attach_other_participant(conversations, user):
    """Annotate each conversation with the other participant, for display."""
    for conversation in conversations:
        conversation.other_user = conversation.other_participant(user)

    return conversations
