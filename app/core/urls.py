"""
Urls for core app.
"""

from core.views import health_check
from django.urls import path

app_name = "core"

urlpatterns = [
    path("health/", health_check, name="health-check"),
]
