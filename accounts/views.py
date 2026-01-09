from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect


@login_required
def after_login(request):
    user = request.user
    if user.role in ("TEACHER", "ADMIN"):
        return redirect("/teacher/")
    return redirect("/dashboard/")


def role_gate(request, allowed_roles: tuple[str, ...], redirect_to: str = "/login/"):
    """
    Login olduktan sonra rol uygun değilse çıkış yaptır ve doğru giriş sayfasına at.
    """
    if not request.user.is_authenticated:
        return None  # gate yok

    if getattr(request.user, "role", None) not in allowed_roles:
        logout(request)
        messages.error(request, "Bu sayfadan giriş yetkin yok. Doğru giriş ekranını kullan.")
        return redirect(redirect_to)

    return None


@login_required
def gate_student(request):
    resp = role_gate(request, ("STUDENT",), "/login/student/")
    return resp or redirect("/dashboard/")


@login_required
def gate_teacher(request):
    resp = role_gate(request, ("TEACHER", "ADMIN"), "/login/teacher/")
    return resp or redirect("/teacher/")


@login_required
def gate_admin(request):
    user = request.user

    # ADMIN rolü + staff veya superuser şart
    if getattr(user, "role", None) != "ADMIN" or not (user.is_staff or user.is_superuser):
        logout(request)
        messages.error(request, "Admin girişi için yetkin yok.")
        return redirect("/login/admin/")

    return redirect("/manager/")

def logout_get(request):
    logout(request)
    return redirect("/login/student/")