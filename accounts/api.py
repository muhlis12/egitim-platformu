from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_search(request):
    q = (request.GET.get("q") or "").strip()
    role = (request.GET.get("role") or "").strip().upper()

    qs = User.objects.all()

    if role:
        qs = qs.filter(role=role)

    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))

    qs = qs.order_by("username")[:25]

    return Response({
        "results": [{"id": u.id, "text": f"{u.username} ({u.first_name} {u.last_name})".strip()} for u in qs]
    })

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class DailyPlanAssignForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Öğrenci"
    )

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

    topic = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Konu (opsiyonel)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # query’leri burada set edelim (import/circular riskini azaltır)
        self.fields["student"].queryset = User.objects.filter(role="STUDENT").order_by("username")

        from .models import TopicTemplate
        self.fields["topic"].queryset = TopicTemplate.objects.all().order_by("id")

    def clean(self):
        cleaned = super().clean()
        typ = cleaned.get("type")
        title = (cleaned.get("title") or "").strip()
        topic = cleaned.get("topic")

        # Başlık boşsa otomatik üret
        if not title:
            label_map = {
                "review": "Tekrar",
                "topic": "Yeni Konu",
                "video": "Video",
                "test": "Mini Test",
                "custom": "Görev",
            }
            base = label_map.get(typ, "Görev")
            if topic:
                cleaned["title"] = f"{base}: {topic.title}"
            else:
                cleaned["title"] = base

        return cleaned
