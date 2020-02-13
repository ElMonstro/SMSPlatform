from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allows access only to 'is_superuser' users
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsOwnerorSuperuser(BasePermission):
    """Allows access to owners or superusers"""

    def has_permission(self, request, view, obj):
        return (
            request.user and request.user.is_superuser or request.user == obj.requester
        )


class IsComapanyOwned(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.company == request.user.company

class IsAdmin(BasePermission):
    """
    Allows access only to 'is_superuser' users
    """

    def has_permission(self, request, view):
        return request.user.is_admin
