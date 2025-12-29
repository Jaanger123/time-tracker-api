from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register('statuses', ProjectStatusViewSet)
router.register('service-lines', ServiceLineViewSet)
router.register('task-types', TaskTypeViewSet)
router.register('tasks', TaskViewSet)


urlpatterns = [
    path('', ProjectListView.as_view(), name='projects-list'),

    # ViewSets
    path('', include(router.urls))
]
