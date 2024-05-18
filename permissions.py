from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, *args, **kwargs):
        print('#'*90)
        print(request)
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True
        return False
    


# class DeletePermission(permissions.BasePermission):
#     message = 'just superuser can call DELETE method!!' # optional

#     def has_permissions(self, request, *args, **kwargs):
#         print('&'*90)
#         print(request.method)

#         if request.user and request.user.is_authenticated:

#             if request.method == 'DELETE':
#                 return request.user.is_superuser
            
#             print('*'*90)
#             print(request.method)
            
#             return True
        
#         return False
    
    
