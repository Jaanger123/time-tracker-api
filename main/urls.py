from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin

from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title='Time-Tracker API',
      default_version='v1',
      description='Test description',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/calendars/', include('apps.calendars.urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns.append(path('api/docs/', schema_view.with_ui()))

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )