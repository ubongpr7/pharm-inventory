from rest_framework import permissions

class HasModelRequestPermission(permissions.BasePermission):
    """
    Checks for both company access AND specific permissions
    """
    def has_permission(self, request, view):
        if request.user.profile.owner == request.user:
            return True

        permission = getattr(view, 'required_permission', None)
        try:

            if  request.user.profile == request.user.company:
                return True
        except Exception as e:
            print(e)
        user_perms=set()
        user_perms.update(request.user.custom_permissions.all().values_list('codename', flat=True))
        try:
            roles=request.user.roles.all()
            for role in roles:
                user_perms.update(role.role.permissions.all().values_list('codename', flat=True))
        except Exception as e:
            print(e)
        try:
            groups=request.user.staff_groups.all()
            for group in groups:
                user_perms.update(group.permissions.all().values_list('codename', flat=True))
        except Exception as e:
            print(e)
    
        if permission:
         
            if isinstance(permission, dict):
                action = view.action
                print(action)
                permission= permission.get(action)
            return permission in user_perms

            
        return False
