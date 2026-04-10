from django.contrib import admin

from .models import *


admin.site.register(ProjectStatus)
admin.site.register(ProjectCode)
admin.site.register(ServiceLine)
admin.site.register(TaskType)
admin.site.register(Project)
admin.site.register(Task)