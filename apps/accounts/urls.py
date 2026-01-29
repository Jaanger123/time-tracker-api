from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from .views import *


router = DefaultRouter()
router.register('users', UserViewSet)
router.register('roles', RoleViewSet)
router.register('positions', PositionViewSet)
router.register('grades', GradeViewSet)
router.register('departments', DepartmentViewSet)
router.register('department-roles', DepartmentRoleViewSet)
router.register('countries', CountryViewSet)

urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    path('activate/', ActivateUserAPIView.as_view(), name='activate_account'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ViewSets
    path('', include(router.urls))
]
