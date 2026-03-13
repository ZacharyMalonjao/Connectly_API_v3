from rest_framework.permissions import BasePermission
#this class becomes vestigial
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
#Admin Posts
class IsPostAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.role == 'admin'  # only admins can delete
        return True  # GET is allowed; privacy handled separately

#For viewing posts from users and guests    
class PostPrivacyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
            if request.user.role == 'admin':
                return True
            if obj.privacy == 'public':
                return True
            # private posts can be seen only by author
            return obj.author == request.user
#For Admin Only comment deletion
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"
    
#To Block guests from posting but temporary class
class IsUserOrAdmin(BasePermission):
 
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ["user", "admin"]