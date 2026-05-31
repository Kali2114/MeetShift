"""
Views for meeting app.
"""

from core.models import Meeting, MeetingParticipant
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from meeting.forms import InviteParticipantForm, MeetingForm
from meeting.utils import user_meetings_queryset


class IndexView(LoginRequiredMixin, TemplateView):
    """Index view for logged-in user."""

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Return meetings for current user."""
        context = super().get_context_data(**kwargs)
        context["meetings"] = user_meetings_queryset(self.request.user)

        return context


class MeetingListView(LoginRequiredMixin, ListView):
    """List meetings participates by logged-in user."""

    model = Meeting
    template_name = "meeting/meeting_list.html"
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
    form_class = MeetingForm
    template_name = "meeting/meeting_form.html"

    def form_valid(self, form):
        """Set organizer as current user."""
        form.instance.organizer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return invite participant after creating meeting."""
        return reverse("meeting:invite-participant", args=[self.object.id])


class EditMeetingView(LoginRequiredMixin, UpdateView):
    """Edit meeting view."""

    model = Meeting
    form_class = MeetingForm
    template_name = "meeting/meeting_form.html"

    def get_queryset(self):
        """Return meeting detail by current user."""
        return Meeting.objects.filter(organizer=self.request.user)

    def get_success_url(self):
        return reverse("meeting:detail-meeting", args=[self.object.id])


class DeleteMeetingView(LoginRequiredMixin, DeleteView):
    """Delete meeting view."""

    model = Meeting
    template_name = "meeting/meeting_confirm_delete.html"
    success_url = reverse_lazy("meeting:list")

    def get_queryset(self):
        """Return only meetings organized by current user."""
        return Meeting.objects.filter(organizer=self.request.user)


class InviteParticipantView(LoginRequiredMixin, FormView):
    """Invite participant view."""

    template_name = "meeting/invite_participant.html"
    form_class = InviteParticipantForm

    def dispatch(self, request, *args, **kwargs):
        """Check meeting exists and current user is organizer."""
        self.meeting = get_object_or_404(
            Meeting,
            id=self.kwargs["pk"],
            organizer=self.request.user,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Invite user to meeting."""
        for user in form.cleaned_data["users"]:
            MeetingParticipant.objects.create(
                meeting=self.meeting,
                user=user,
            )

        return redirect("meeting:detail-meeting", pk=self.meeting.id)

    def get_form_kwargs(self):
        """Pass meeting to invite form."""
        kwargs = super().get_form_kwargs()
        kwargs["meeting"] = self.meeting
        return kwargs


class AcceptInvitationView(LoginRequiredMixin, View):
    """Accept invitation view."""

    def post(self, request, *args, **kwargs):
        """Accept current user invitation."""
        invitation = get_object_or_404(
            MeetingParticipant,
            id=self.kwargs["pk"],
            user=request.user,
        )
        invitation.invitation_status = "ACC"
        invitation.save()

        return redirect(request.POST.get("next", "meeting:invitations"))


class DeclineInvitationView(LoginRequiredMixin, View):
    """Decline invitation view."""

    def post(self, request, *args, **kwargs):
        """Decline current user invitation."""
        invitation = get_object_or_404(
            MeetingParticipant,
            id=self.kwargs["pk"],
            user=request.user,
        )
        invitation.invitation_status = "DEC"
        invitation.save()

        return redirect(request.POST.get("next", "meeting:invitations"))


class InvitationListView(LoginRequiredMixin, ListView):
    """List current user invitations."""

    model = MeetingParticipant
    template_name = "invitations/invitations.html"
    context_object_name = "invitations"

    def get_queryset(self):
        """Return current user invitations."""
        return MeetingParticipant.objects.filter(user=self.request.user)
