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


class IsCompanyOwned(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.company == request.user.company

class IsAdmin(BasePermission):
    """
    Allows access only to 'is_admin' users
    """
    message = "Only admins are allowed to access this resource. Please contat your admin to elevate your permissions"

    def has_permission(self, request, view):
        return request.user.is_admin


class IsDirector(BasePermission):
    """
    Allows access only to 'is_director' users
    """
    message = "Only directors are allowed to access this resource."

    def has_permission(self, request, view):
        return request.user.is_director

class IsReseller(BasePermission):
    """
    Allows access only to 'is_director' users
    """
    message = "Only resellers are allowed to access this resource."

    def has_permission(self, request, view):
        return request.user.is_reseller


class IsVerified(BasePermission):
    """
    Allows access only to 'is_verified' users
    """
    message = "Your account is not verified. Please verify your account for access."

    def has_permission(self, request, view):
        return request.user.is_verified
