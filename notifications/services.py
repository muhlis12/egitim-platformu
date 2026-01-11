from .models import Notification

def notify(user, title, body="", url="", level="info"):
    Notification.objects.create(
        user=user,
        title=title,
        body=body,
        url=url,
        level=level
    )
