from django.urls import path
from .views import purchase_request_create

urlpatterns = [
    path("payments/course/<int:course_id>/request/", purchase_request_create, name="purchase_request_create"),
]
