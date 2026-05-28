"""
Forms for meeting app.
"""

from core.models import Meeting
from django import forms


class MeetingForm(forms.ModelForm):
    """Form for create meetings."""

    class Meta:
        model = Meeting
        fields = ["title", "description", "started_at", "ended_at"]
        widgets = {
            "started_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ended_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        """Validate meeting end time is after start time."""
        cleaned_data = super().clean()
        started_at = cleaned_data.get("started_at")
        ended_at = cleaned_data.get("ended_at")

        if started_at and ended_at and ended_at <= started_at:
            raise forms.ValidationError("End time must be after start time.")

        return cleaned_data
