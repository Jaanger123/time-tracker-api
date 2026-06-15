from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView
)

from .views import *


router = DefaultRouter()
router.register('users', UserViewSet)
router.register('statuses', UserStatusViewSet)
router.register('status-history', UserStatusHistoryViewSet)
router.register('roles', RoleViewSet)
router.register('positions', PositionViewSet)
router.register('grades', GradeViewSet)
router.register('departments', DepartmentViewSet)
router.register('department-roles', DepartmentRoleViewSet)
router.register('countries', CountryViewSet)

urlpatterns = [
    path('activate/', ActivateUserAPIView.as_view(), name='activate_account'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordAPIView.as_view()),
    path('reset-password/', ResetPasswordAPIView.as_view()),

    # ViewSets
    path('', include(router.urls))
]
