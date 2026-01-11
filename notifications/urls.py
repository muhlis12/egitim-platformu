from django.urls import path
from .api import my_notifications, mark_read, mark_all_read

urlpatterns = [
    path("api/v1/notifications", my_notifications, name="api_notifications"),
    path("api/v1/notifications/<int:nid>/read", mark_read, name="api_notification_read"),
    path("api/v1/notifications/read-all", mark_all_read, name="api_notification_read_all"),
]
