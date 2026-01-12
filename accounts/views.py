from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def login_choice(request):
    return render(request, "accounts/login_choice.html")


@login_required
def after_login(request):
    role = getattr(request.user, "role", None)

    if role == "ADMIN":
        return redirect("/manager/")

    if role == "TEACHER":
        return redirect("/teacher/")

    if role == "PARENT":
        return redirect("/parent/")

    # STUDENT ve diğerleri
    return redirect("/dashboard/")


def role_gate(request, allowed_roles: tuple, redirect_to: str = "/login/"):
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
    resp = role_gate(request, ("TEACHER", "ADMIN"), "/login/teacher/")
    return resp or redirect("/teacher/")


@login_required
def gate_parent(request):
    resp = role_gate(request, ("PARENT",), "/login/parent/")
    return resp or redirect("/parent/")


@login_required
def gate_admin(request):
    """
    Admin girişi:
    - Custom /login/admin/ ekranında "yetkin yok" hatası almamak için
      Django'nun kendi yetkisini (is_staff / is_superuser) baz alıyoruz.
    - Role sistemi varsa, role "ADMIN" değil diye admini kilitlemeyelim.
    """
    user = request.user

    # Django admin yetkisi yoksa admin paneline sokma
    if not (user.is_staff or user.is_superuser):
        logout(request)
        messages.error(request, "Admin girişi için yetkin yok.")
        return redirect("/login/admin/")

    # İstersen superuser ise role otomatik ADMIN yap (opsiyonel)
    # if user.is_superuser and getattr(user, "role", None) != "ADMIN":
    #     user.role = "ADMIN"
    #     user.save(update_fields=["role"])

    return redirect("/manager/")


def logout_get(request):
    logout(request)
    return redirect("/login/")
