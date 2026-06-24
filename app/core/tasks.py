"""
Tasks for app.
"""

from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_invitation_email_task(user_email, meeting_title):
    """Send invitation email asynchronously."""
    send_mail(
        subject="Meeting Invitation",
        message=f"Invitation for {meeting_title}",
        from_email=None,
        recipient_list=[user_email],
    )


@shared_task
def send_activation_email_task(user_email, activation_link):
    """Send activation email asynchronously."""
    send_mail(
        subject="Activate your MeetShift account",
        message=f"Click the link below to activate your MeetShift "
        f"account:\n\n{activation_link}",
        from_email=None,
        recipient_list=[user_email],
    )
