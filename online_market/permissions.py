from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsAdminUserOrObjectCreator(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and request.user.is_staff or
            request.user == obj.user
        )


class IsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
