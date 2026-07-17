"""
Configuration for user app.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    def ready(self):
        """Load user application signals."""
        import core.signals  # noqa: F401
