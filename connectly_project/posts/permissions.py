from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    """
    Custom permission to only allow authors of a post to edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # obj is the Post instance
        # Only allow the author of the post to have permission
        return obj.author == request.user
"""
RBAC Permissions guide
 Role    Can View         Can Create   Can Delete
---------------------------------------------
Guest  |  Public           |  no     |   no
User   |  Public/Own posts |  yes    |   no
Admin  |  All Posts        |  yes    |   yes
"""

class IsPostAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin can access all posts
        if request.user.role == 'admin':
            return True
        # Authors can access their own posts
        return obj.author == request.user
    
class PostPrivacyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if obj.privacy == 'public':
            return True
        # Private posts can be seen only by author
        return obj.author == request.user