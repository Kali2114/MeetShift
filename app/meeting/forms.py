"""
Forms for meeting app.
"""

from core.models import Meeting, User
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

    def clean_email(self):
        """Validate invited user email."""
        email = self.cleaned_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")

        if user == self.meeting.organizer:
            raise forms.ValidationError("You cannot invite yourself.")

        if self.meeting.participants.filter(user=user).exists():
            raise forms.ValidationError("You are already invited.")

        self.cleaned_data["user"] = user
        return email
