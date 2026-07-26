"""
Forms for meeting app.
"""

from core.models import Meeting, RoomMessage, User
from django import forms


class MeetingForm(forms.ModelForm):
    """Form for create meetings."""

    class Meta:
        model = Meeting
        fields = ["title", "description", "started_at", "ended_at"]
        widgets = {
            "started_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "ended_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def clean(self):
        """Validate meeting end time is after start time."""
        cleaned_data = super().clean()
        started_at = cleaned_data.get("started_at")
        ended_at = cleaned_data.get("ended_at")

        if started_at and ended_at and ended_at <= started_at:
            raise forms.ValidationError("End time must be after start time.")

        return cleaned_data


class InviteParticipantForm(forms.Form):
    """Form for invite participants."""

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with meeting."""
        self.meeting = kwargs.pop("meeting")
        super().__init__(*args, **kwargs)

        self.fields["users"].queryset = User.objects.exclude(
            id=self.meeting.organizer.id
        ).exclude(meeting_participations__meeting=self.meeting)


class RoomMessageForm(forms.ModelForm):
    """Form for sending a message in a meeting room."""

    class Meta:
        model = RoomMessage
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 1, "placeholder": "Write a message..."}
            ),
        }
