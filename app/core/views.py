"""
Views for core app.
"""

from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Return application health check including database connection."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")

    return JsonResponse({"status": "ok", "database": "ok"})
