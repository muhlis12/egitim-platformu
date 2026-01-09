from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course, Enrollment
from .models import PurchaseRequest

@login_required
def purchase_request_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "STUDENT":
        messages.error(request, "Sadece öğrenciler satın alma talebi oluşturabilir.")
        return redirect(f"/courses/{course.id}/")

    pr, created = PurchaseRequest.objects.get_or_create(user=request.user, course=course)
    if pr.status == PurchaseRequest.Status.APPROVED:
        messages.success(request, "Bu kurs zaten onaylanmış.")
        return redirect(f"/courses/{course.id}/")

    messages.success(request, "Satın alma talebin alındı. Onaydan sonra kurs açılacak.")
    return redirect("/dashboard/")
