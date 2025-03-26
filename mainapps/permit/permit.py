from rest_framework import permissions

class HasModelRequestPermission(permissions.BasePermission):
    """
    Checks for both company access AND specific permissions
    """
    def has_permission(self, request, view):
        permission = getattr(view, 'required_permission', None)
        
        if not request.user.profile or request.user.profile.company != view.get_company():
            return False
            
        if permission:
            if isinstance(permission, dict):
                action = view.action
                return request.user.has_custom_perm(permission.get(action))
            return request.user.has_custom_perm(permission)
            
        return True

    # def has_object_permission(self, request, view, obj):

    #     return obj.company == request.user.profile