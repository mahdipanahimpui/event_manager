from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True
        return False
    


    
    
