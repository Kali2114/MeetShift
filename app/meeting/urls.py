"""
Urls mapping for the meeting app.
"""

from django.urls import path
from meeting import views

app_name = "meeting"


urlpatterns = [
    path("", views.MeetingListView.as_view(), name="list"),
]
