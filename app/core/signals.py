"""
Signals for app.
"""

from core.models import User, UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile after user creation."""
    if created:
        UserProfile.objects.create(user=instance)
