from django.contrib import admin
from .models import Grade, Subject, TopicTemplate
from .models import TopicContent, TopicQuestion, StudentTopicProgress

admin.site.register(Grade)
admin.site.register(Subject)
admin.site.register(TopicTemplate)
admin.site.register(TopicContent)
admin.site.register(TopicQuestion)
admin.site.register(StudentTopicProgress)
