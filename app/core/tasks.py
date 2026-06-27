"""
Tasks for app.
"""

import logging

from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task
def send_invitation_email_task(user_email, meeting_title):
    """Send invitation email asynchronously."""
    try:
        send_mail(
            subject="Meeting Invitation",
            message=f"Invitation for {meeting_title}",
            from_email=None,
            recipient_list=[user_email],
        )
        logger.info(
            "Invitation email sent: user_email=%s meeting_title=%s",
            user_email,
            meeting_title,
        )
    except Exception:
        logger.exception(
            "Invitation email failed: user_email=%s meeting_title=%s",
            user_email,
            meeting_title,
        )
        raise


@shared_task
def send_activation_email_task(user_email, activation_link):
    """Send activation email asynchronously."""
    try:
        send_mail(
            subject="Activate your MeetShift account",
            message=f"Click the link below to activate your MeetShift "
            f"account:\n\n{activation_link}",
            from_email=None,
            recipient_list=[user_email],
        )
        logger.info(
            "Activation email sent: user_email=%s",
            user_email,
        )
    except Exception:
        logger.exception(
            "Activation email failed: user_email=%s",
            user_email,
        )
        raise
