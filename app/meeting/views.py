"""
Views for meeting app.
"""

from core.models import Meeting
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from meeting.utils import user_meetings_queryset


class MeetingListView(LoginRequiredMixin, ListView):
    """List meetings participates by logged-in user."""

    model = Meeting
    template_name = "meeting/meeting.html"
    context_object_name = "meetings"

    def get_queryset(self):
        """Return meetings participates by current user."""
        return user_meetings_queryset(self.request.user)


class MeetingDetailView(LoginRequiredMixin, DetailView):
    """Detail meeting view for logged-in user."""

    model = Meeting
    template_name = "meeting/meeting_details.html"
    context_object_name = "meeting"

    def get_queryset(self):
        """Return meeting detail by current user"""
        return user_meetings_queryset(self.request.user)


class CreateMeetingView(LoginRequiredMixin, CreateView):
    """Create meeting view."""

    model = Meeting
    fields = ["title", "description"]
    template_name = "meeting/meeting_form.html"
    success_url = reverse_lazy("meeting:list")

    def form_valid(self, form):
        """Set organizer as current user."""
        form.instance.organizer = self.request.user
        return super().form_valid(form)


class EditMeetingView(LoginRequiredMixin, UpdateView):
    """Edit meeting view."""

    model = Meeting
    fields = ["title", "description"]
    template_name = "meeting/meeting_form.html"

    def get_queryset(self):
        """Return meeting detail by current user."""
        return Meeting.objects.filter(organizer=self.request.user)

    def get_success_url(self):
        return reverse("meeting:detail-meeting", args=[self.object.id])
