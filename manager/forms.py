from django import forms
from django.contrib.auth import get_user_model
from courses.models import Course
from content.models import Grade, Subject

User = get_user_model()

class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]

class AssignTeacherForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role="TEACHER"),
        label="Öğretmen"
    )

class EnrollStudentForm(forms.Form):
    username = forms.CharField(label="Öğrenci kullanıcı adı", max_length=150)

class ReadyLessonsForm(forms.Form):
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(), label="Sınıf")
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), label="Ders")
