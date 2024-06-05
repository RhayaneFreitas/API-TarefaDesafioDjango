from django.contrib import admin

from api.apps.task.models import task

admin.site.register(task.TaskProfile)
admin.site.register(task.TaskResponsible)
