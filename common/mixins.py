from rest_framework.permissions import IsAuthenticated

from .permissions import IsAdminRole


class AdminWritePermissionMixin:
    admin_actions = {
        'create',
        'update',
        'partial_update',
        'destroy',
    }

    def get_permissions(self):
        if self.action in self.admin_actions:
            return [IsAdminRole()]

        return [IsAuthenticated()]