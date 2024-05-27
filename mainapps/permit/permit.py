from django.contrib.auth.models import Permission,Group
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from mainapps.permit.permission_decorators import group_required

# @permission_required('app_label.permision_model')
# @permission_required('accounts.view_user')



from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps



User= settings.AUTH_USER_MODEL
# @login_required
def add_to_permision_group(group_name,username):
    group,created =Group.objects.get_or_create(name=group_name)
    user = User.objects.get(username=username)
    user.groups.add(group)
    return user

def get_all_permissions():
    all_permissions= Permission.objects.all()
    for i in range(0,len(all_permissions)):
        print(f'All-> {i}: {all_permissions[i]}')
    print('done')
    return all_permissions


def get_model_permission(model_class):
    content_type= ContentType.objects.get_for_model(model_class).model_class()
    print(content_type)
    
    model_permissions= Permission.objects.filter(content_type)
    print(model_permissions)
    for i in range(0,len(model_permissions)):
        print(f'{i}: {model_permissions[i]}')

    return model_permissions


# @group_required
# def assure_permission_by_group(model_item,request,group_name):
#     user= request.user
#     if user.groups.filter(name=group_name).exist():
#         return model_item

def assure_permission(model_item,request,group_name):
    user= request.user
    if user.has_perm('app_label.permission_model'):
        return model_item
    
def create_group_with_group_name(request):
    group_name=request.group_name
    group,created =Group.objects.get_or_create(name=group_name)
    group.permissions.add()