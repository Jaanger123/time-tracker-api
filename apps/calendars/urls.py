from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register('time-entries', TimeEntryViewSet)
router.register('calendars', CalendarViewSet)

urlpatterns = [
    path('settings/', CountrySettingsView.as_view(), name='global-settings'),

    # ViewSets
    path('', include(router.urls)),
]
