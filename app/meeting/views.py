"""
Views for meeting app.
"""

import logging

from core.models import Meeting, MeetingParticipant, RoomMessage
from core.tasks import send_invitation_email_task
from django.contrib import messages
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
from meeting.forms import InviteParticipantForm, MeetingForm, RoomMessageForm
from meeting.utils import (
    meeting_calendar_events,
    online_room_users,
    user_accessible_room_meetings,
    user_has_meeting_conflict,
    user_meetings_queryset,
)
from user.services import create_notification

logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, TemplateView):
    """Index view for logged-in user."""

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Return calendar events for current user's meetings."""
        context = super().get_context_data(**kwargs)
        context["calendar_events"] = meeting_calendar_events(self.request.user)

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

    def get_context_data(self, **kwargs):
        """Attach whether the current user can enter the meeting's room."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["can_enter_room"] = (
            self.object.organizer == user
            or self.object.participants.filter(
                user=user, invitation_status="ACC"
            ).exists()
        )

        return context


class CreateMeetingView(LoginRequiredMixin, CreateView):
    """Create meeting view."""

    model = Meeting
    form_class = MeetingForm
    template_name = "meeting/meeting_form.html"

    def form_valid(self, form):
        """Set organizer as current user."""
        form.instance.organizer = self.request.user
        response = super().form_valid(form)

        logger.info(
            "Meeting created: meeting_id=%s organizer_id=%s organizer_email=%s",
            self.object.id,
            self.request.user.id,
            self.request.user.email,
        )

        return response

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
        invited_users = form.cleaned_data["users"]

        for user in invited_users:
            MeetingParticipant.objects.create(
                meeting=self.meeting,
                user=user,
            )
            create_notification(
                meeting=self.meeting,
                user=user,
                message=f"You have been invited to meeting: {self.meeting}",
            )

            send_invitation_email_task.delay(user.email, self.meeting.title)

            logger.info(
                "User invited to meeting: meeting_id=%s organizer_id=%s "
                "invited_user_id=%s invited_user_email=%s",
                self.meeting.id,
                self.request.user.id,
                user.id,
                user.email,
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
        if user_has_meeting_conflict(request.user, invitation.meeting):
            logger.warning(
                "Invitation accept blocked by conflict: meeting_id=%s "
                "user_id=%s invitation_id=%s",
                invitation.meeting.id,
                request.user.id,
                invitation.id,
            )
            messages.error(
                request, "You already have another accepted meeting at this time."
            )
            return redirect(request.POST.get("next", "meeting:invitations"))
        invitation.invitation_status = "ACC"
        invitation.save()
        logger.info(
            "Invitation accepted: meeting_id=%s user_id=%s invitation_id=%s",
            invitation.meeting.id,
            request.user.id,
            invitation.id,
        )

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
        logger.info(
            "Invitation declined: meeting_id=%s user_id=%s invitation_id=%s",
            invitation.meeting.id,
            request.user.id,
            invitation.id,
        )

        return redirect(request.POST.get("next", "meeting:invitations"))


class InvitationListView(LoginRequiredMixin, ListView):
    """List current user invitations."""

    model = MeetingParticipant
    template_name = "invitations/invitations.html"
    context_object_name = "invitations"

    def get_queryset(self):
        """Return current user invitations."""
        return MeetingParticipant.objects.filter(user=self.request.user)


class RoomDetailView(LoginRequiredMixin, DetailView):
    """Room detail view."""

    model = Meeting
    template_name = "meeting/room_detail.html"

    def get_queryset(self):
        """Return meetings whose room the current user can access."""
        return user_accessible_room_meetings(self.request.user)

    def get_context_data(self, **kwargs):
        """Attach the room's message form and currently online users."""
        context = super().get_context_data(**kwargs)
        context["message_form"] = RoomMessageForm()
        context["online_users"] = online_room_users(self.object.room)

        return context


class SendRoomMessageView(LoginRequiredMixin, View):
    """Send a message in a meeting's room."""

    def post(self, request, pk):
        """Create the message if valid and the room is active."""
        meeting = get_object_or_404(user_accessible_room_meetings(request.user), pk=pk)

        if not meeting.room.is_active():
            messages.error(request, "This room is not active.")
            return redirect("meeting:room-detail", pk=meeting.id)

        form = RoomMessageForm(request.POST)

        if form.is_valid():
            RoomMessage.objects.create(
                room=meeting.room,
                sender=request.user,
                content=form.cleaned_data["content"],
            )

            logger.info(
                "Room message sent: meeting_id=%s sender_id=%s",
                meeting.id,
                request.user.id,
            )
        else:
            messages.error(request, "Message cannot be empty.")

        return redirect("meeting:room-detail", pk=meeting.id)
