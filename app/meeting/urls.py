"""
Urls mapping for the meeting app.
"""

from django.urls import path
from meeting import views

app_name = "meeting"


urlpatterns = [
    path("meetings/", views.MeetingListView.as_view(), name="list"),
    path(
        "meetings/<int:pk>/", views.MeetingDetailView.as_view(), name="detail-meeting"
    ),
    path(
        "meeting_form/",
        views.CreateMeetingView.as_view(),
        name="create-meeting",
    ),
    path(
        "meeting_edit/<int:pk>/", views.EditMeetingView.as_view(), name="edit-meeting"
    ),
    path(
        "meeting_delete/<int:pk>/",
        views.DeleteMeetingView.as_view(),
        name="delete-meeting",
    ),
]
