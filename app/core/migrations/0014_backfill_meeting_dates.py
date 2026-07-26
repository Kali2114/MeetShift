from datetime import timedelta

from django.db import migrations


def backfill_meeting_dates(apps, schema_editor):
    """Fill any meeting missing started_at/ended_at with a placeholder schedule."""
    Meeting = apps.get_model("core", "Meeting")

    for meeting in Meeting.objects.filter(started_at__isnull=True):
        meeting.started_at = meeting.created_at
        meeting.save(update_fields=["started_at"])

    for meeting in Meeting.objects.filter(ended_at__isnull=True):
        meeting.ended_at = meeting.started_at + timedelta(hours=1)
        meeting.save(update_fields=["ended_at"])


def noop_reverse(apps, schema_editor):
    """No-op reverse: backfilled placeholder dates aren't worth reverting."""


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_notification_conversation"),
    ]

    operations = [
        migrations.RunPython(backfill_meeting_dates, noop_reverse),
    ]
