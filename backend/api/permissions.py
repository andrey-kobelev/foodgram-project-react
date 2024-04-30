from rest_framework import permissions


class AdminUserSafeMethods(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (obj == request.user or request.user.is_admin)
        )


class AdminAuthorSafeMethods(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (obj.author == request.user or request.user.is_admin)
        )
