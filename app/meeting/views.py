"""
Views for meeting app.
"""

from core.models import Meeting
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView


class MeetingListView(LoginRequiredMixin, ListView):
    """List meetings participates by logged-in user"""

    model = Meeting
    template_name = "meeting/meeting.html"
    context_object_name = "meetings"

    def get_queryset(self):
        """Return meetings participates by current user."""
        queryset = Meeting.objects.filter(
            Q(organizer=self.request.user) | Q(participants__user=self.request.user)
        ).distinct()
        return queryset
