"""
Forms for meeting app.
"""

from core.models import Meeting
from django import forms


class MeetingForm(forms.ModelForm):
    """Form for create meetings."""

    class Meta:
        model = Meeting
        fields = ["title", "description", "started_at"]
        widgets = {
            "started_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
