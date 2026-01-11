from django import forms
from django.utils import timezone


class DailyPlanAssignForm(forms.Form):
    # Select2 AJAX ile seçilecek
    student_id = forms.IntegerField()
    topic_id = forms.IntegerField(required=False)

    date = forms.DateField(
        label="Tarih",
        initial=timezone.localdate,
        required=True
    )

    type = forms.ChoiceField(
        choices=[
            ("review", "Tekrar"),
            ("topic", "Konu"),
            ("video", "Video"),
            ("test", "Test"),
            ("custom", "Özel"),
        ],
        label="Görev tipi"
    )

    title = forms.CharField(
        label="Başlık",
        max_length=255,
        required=False,
        help_text="Boş bırakılırsa otomatik doldurulur."
    )

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"]
        if not sid or sid <= 0:
            raise forms.ValidationError("Öğrenci seçilmedi.")
        return sid

    def clean_topic_id(self):
        tid = self.cleaned_data.get("topic_id")
        if tid in (None, "", 0):
            return None
        try:
            tid = int(tid)
        except ValueError:
            raise forms.ValidationError("Konu id geçersiz.")
        if tid <= 0:
            return None
        return tid
