from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read-only methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Admin can do anything
        if request.user.is_staff:
            return True

        # User can modify only their own objects
        return obj.user == request.user
