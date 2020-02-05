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


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
