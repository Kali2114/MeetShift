"""
Utils functions for app.
"""

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def check_email_and_name(email, name):
    """Validate that both email and name are provided and email is well-formed."""
    if not email:
        raise ValueError("Email is required.")
    if not name:
        raise ValueError("Name is required.")
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError("A valid email is required.")
