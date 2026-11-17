"""Object-level ownership permission for tasks."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsTaskOwner(BasePermission):
    """Allow access only when the object's owner is the requesting user.

    List endpoints already scope to ``request.user``; this guards detail routes.
    Foreign tasks produce 404 via ``get_object`` semantics.
    """

    def has_object_permission(self, request, view, obj):
        if not getattr(obj, "owner_id", None):
            return False
        if request.method in SAFE_METHODS:
            return obj.owner_id == request.user.id
        return obj.owner_id == request.user.id
