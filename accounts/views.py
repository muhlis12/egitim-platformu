from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def login_choice(request):
    """
    /login/ -> 4 kutulu giriş seçim ekranı
    """
    return render(request, "accounts/login_choice.html")


@login_required
def after_login(request):
    """
    Login sonrası tek yerden yönlendirme (PRO)
    """
    role = getattr(request.user, "role", None)

    if role == "ADMIN":
        return redirect("/manager/")

    if role == "TEACHER":
        return redirect("/teacher/")

    if role == "PARENT":
        return redirect("/dashboard/")  # ileride /parent/ yaparız

    # STUDENT ve diğerleri
    return redirect("/dashboard/")


def role_gate(request, allowed_roles: tuple, redirect_to: str = "/login/"):
    """
    Login olduktan sonra rol uygun değilse çıkış yaptır ve doğru giriş sayfasına at.
    """
    if not request.user.is_authenticated:
        return None

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
    # Öğretmen paneline admin de girebilsin istiyorsan bırak
    resp = role_gate(request, ("TEACHER", "ADMIN"), "/login/teacher/")
    return resp or redirect("/teacher/")


@login_required
def gate_parent(request):
    resp = role_gate(request, ("PARENT",), "/login/parent/")
    return resp or redirect("/dashboard/")  # ileride /parent/


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
    return redirect("/login/")
