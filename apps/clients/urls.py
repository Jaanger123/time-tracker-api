from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register('sectors', SectorViewSet)
router.register('pies', PieViewSet)
router.register('clients', ClientViewSet)

urlpatterns = [
    # ViewSets
    path('', include(router.urls))
]
