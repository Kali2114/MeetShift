from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_backfill_meeting_dates"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meeting",
            name="started_at",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="ended_at",
            field=models.DateTimeField(),
        ),
    ]
