from django.contrib import admin

from api.apps.task.models import user

admin.site.register(user.TaskProfile)
admin.site.register(user.TaskResponsible)
