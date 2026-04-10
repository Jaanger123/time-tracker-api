from django.contrib import admin

from .models import *


@admin.register(CountrySettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    pass

admin.site.register(TimeEntry)
admin.site.register(Calendar)
