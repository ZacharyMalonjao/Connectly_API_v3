from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    """
    Custom permission to only allow authors of a post to edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # obj is the Post instance
        # Only allow the author of the post to have permission
        return obj.author == request.user