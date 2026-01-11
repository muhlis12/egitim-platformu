from django import forms
from django.contrib.auth import get_user_model

from courses.models import Course
from content.models import Grade, Subject   # ✅ EKSİK OLAN BUYDU

User = get_user_model()


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ("owner",)  # owner formdan gelmesin


class AssignTeacherForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role="TEACHER"),
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
