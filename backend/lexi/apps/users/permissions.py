from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

class IsProfileCompleted(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.profile_completed:
            raise PermissionDenied({
                "status": "error",
                "message": "يرجى إكمال ملفك الشخصي أولاً"
            })
        return True