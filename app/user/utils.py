"""
Utils for user app.
"""

from django.contrib.auth.tokens import default_token_generator
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
