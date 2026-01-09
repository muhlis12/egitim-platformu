from django import forms
from courses.models import Course
from content.models import Lesson, LessonFile
from content.models import LessonVideo
from quiz.models import Exam, Question
from live.models import LiveLesson
from django import forms
from content.models import Grade, Subject

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "body", "order"]

class LessonFileForm(forms.ModelForm):
    class Meta:
        model = LessonFile
        fields = ["title", "file"]
        

class LessonVideoForm(forms.ModelForm):
    class Meta:
        model = LessonVideo
        fields = ["title", "video"]
        


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["title", "duration_minutes", "is_active"]

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["order", "text", "choice_a", "choice_b", "choice_c", "choice_d", "correct"]

class LiveLessonForm(forms.ModelForm):
    class Meta:
        model = LiveLesson
        fields = ["title", "meet_link", "start_time", "duration_minutes"]

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class EnrollStudentForm(forms.Form):
    username = forms.CharField(label="Öğrenci kullanıcı adı", max_length=150)

    def clean_username(self):
        uname = self.cleaned_data["username"].strip()
        try:
            u = User.objects.get(username=uname)
        except User.DoesNotExist:
            raise forms.ValidationError("Bu kullanıcı adı bulunamadı.")
        if getattr(u, "role", None) != "STUDENT":
            raise forms.ValidationError("Bu kullanıcı STUDENT rolünde değil.")
        return uname

class AddTopicLessonsForm(forms.Form):
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(), label="Sınıf")
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), label="Ders")