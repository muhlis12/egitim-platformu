from django.utils import timezone

class LastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resp = self.get_response(request)
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            try:
                user.profile.last_seen = timezone.now()
                user.profile.save(update_fields=["last_seen"])
            except Exception:
                pass
        return resp
