from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

class IsProfileCompleted(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.is_profile_completed:
            raise PermissionDenied({
                "status": "error",
                "message": "Please complete your profile first"
            })
        return True