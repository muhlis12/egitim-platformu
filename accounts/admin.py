from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import UserProfile

User = get_user_model()


# ---------------------------
# Custom User Change Form
# ---------------------------
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


# ---------------------------
# UserProfile Inline (WhatsApp)
# ---------------------------
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0
    verbose_name_plural = "WhatsApp / Profil Bilgileri"


# ---------------------------
# Custom User Admin
# ---------------------------
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = CustomUserChangeForm
    inlines = [UserProfileInline]

    # Listede görünen kolonlar
    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("username",)

    # Kullanıcı düzenleme ekranı
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Kişisel Bilgiler", {"fields": ("first_name", "last_name", "email")}),
        ("Rol", {"fields": ("role",)}),
        ("İzinler", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Önemli Tarihler", {"fields": ("last_login", "date_joined")}),
    )

    # Kullanıcı ekleme ekranı (Şifre1 / Şifre2 düzgün çıkar)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "role",
                "password1",
                "password2",
                "is_active",
                "is_staff",
            ),
        }),
    )
