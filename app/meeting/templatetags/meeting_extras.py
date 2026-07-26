"""
Template tags for meeting app.
"""

from django import template
from meeting.utils import sender_color as _sender_color

register = template.Library()


@register.filter
def sender_color(user_id):
    """Return a deterministic room chat display color for a user id."""
    return _sender_color(user_id)
