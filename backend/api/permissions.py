from rest_framework import permissions


class AuthorSafeMethods(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class MePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method == 'GET'
            and request.user.is_authenticated
        )

