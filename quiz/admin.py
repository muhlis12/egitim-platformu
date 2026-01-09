from django.contrib import admin
from .models import Exam, Question, Attempt, Answer

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Attempt)
admin.site.register(Answer)
