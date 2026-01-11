from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TopicTemplate, Grade, Subject


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def topics_search(request):
    """
    /api/v1/topics/search?q=asal&grade=8&subject=Matematik
    """
    q = (request.GET.get("q") or "").strip()
    grade_val = (request.GET.get("grade") or "").strip()
    subject_name = (request.GET.get("subject") or "").strip()

    qs = TopicTemplate.objects.select_related("grade", "subject")

    if q:
        qs = qs.filter(title__icontains=q)

    if grade_val:
        try:
            grade_obj = Grade.objects.get(number=int(grade_val))
            qs = qs.filter(grade=grade_obj)
        except Exception:
            pass

    if subject_name:
        try:
            subject_obj = Subject.objects.get(name=subject_name)
            qs = qs.filter(subject=subject_obj)
        except Exception:
            pass

    qs = qs.order_by("id")[:25]

    return Response({
        "results": [{"id": t.id, "text": f"{t.grade.number} {t.subject.name} - {t.title}"} for t in qs]
    })
