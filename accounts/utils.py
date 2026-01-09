from django.http import HttpResponseForbidden

def role_required(*allowed_roles):
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Login gerekli")
            if getattr(request.user, "role", None) not in allowed_roles:
                return HttpResponseForbidden("Bu sayfaya yetkin yok.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

admin_required = role_required("ADMIN")
teacher_required = role_required("TEACHER", "ADMIN")
student_required = role_required("STUDENT")
