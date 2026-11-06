from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import DepartmentRole


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        return obj.user == request.user


class IsDepartmentManager(BasePermission):
    message = 'Only managers can access this endpoint.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.department_role
            and request.user.department_role.name
            == DepartmentRole.MANAGER
        )
