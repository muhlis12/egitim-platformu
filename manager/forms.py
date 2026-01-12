from django import forms
from django.contrib.auth import get_user_model

from courses.models import Course
from content.models import Grade, Subject

User = get_user_model()


# ---------------------------------
# Helpers
# ---------------------------------
def _sync_staff_flags(user: User):
    """
    Role -> Django admin yetki bayrakları eşlemesi.
    ADMIN: is_staff=True (admin paneline girebilir)
    Diğerleri: staff/superuser kapalı
    """
    role = getattr(user, "role", None)

    if role == "ADMIN":
        user.is_staff = True
        # İstersen adminleri superuser yapma. (Daha güvenli)
        # user.is_superuser = False
    else:
        user.is_staff = False
        user.is_superuser = False


# ---------------------------------
# Courses
# ---------------------------------
class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ("owner",)  # owner formdan gelmesin


class AssignTeacherForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role="TEACHER").order_by("username"),
        label="Öğretmen"
    )


class EnrollStudentForm(forms.Form):
    username = forms.CharField(label="Öğrenci kullanıcı adı", max_length=150)


class ReadyLessonsForm(forms.Form):
    grade = forms.ModelChoiceField(
        queryset=Grade.objects.order_by("number"),
        label="Sınıf"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.order_by("name"),
        label="Ders"
    )


# ---------------------------------
# Admin: User Management
# ---------------------------------
class AdminUserCreateForm(forms.ModelForm):
    password = forms.CharField(label="Şifre", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "role", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        # ✅ role değişince staff bayrağı güncellensin
        _sync_staff_flags(user)

        if commit:
            user.save()
        return user


class AdminUserEditForm(forms.ModelForm):
    new_password = forms.CharField(
        label="Yeni Şifre (opsiyonel)",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "role"]

    def save(self, commit=True):
        user = super().save(commit=False)

        pw = self.cleaned_data.get("new_password")
        if pw:
            user.set_password(pw)

        # ✅ role değişince staff bayrağı güncellensin
        _sync_staff_flags(user)

        if commit:
            user.save()
        return user


# ---------------------------------
# PRO: Student + Parent create & link
# ---------------------------------
class StudentWithParentCreateForm(forms.Form):
    # Öğrenci
    student_username = forms.CharField(label="Öğrenci kullanıcı adı", max_length=150)
    student_first_name = forms.CharField(label="Öğrenci adı", max_length=150, required=False)
    student_last_name = forms.CharField(label="Öğrenci soyadı", max_length=150, required=False)
    student_password = forms.CharField(label="Öğrenci şifre", widget=forms.PasswordInput)

    # Veli
    parent_username = forms.CharField(label="Veli kullanıcı adı", max_length=150)
    parent_first_name = forms.CharField(label="Veli adı", max_length=150, required=False)
    parent_last_name = forms.CharField(label="Veli soyadı", max_length=150, required=False)
    parent_password = forms.CharField(label="Veli şifre", widget=forms.PasswordInput)
