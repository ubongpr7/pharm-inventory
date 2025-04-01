from django.urls import path
from .views import UserPermissionManager,GroupPermissionManager

urlpatterns = [
    path(
        'users/<str:pk>/permissions/',
        UserPermissionManager.as_view(),
        name='user-permissions-manage'
    ),
    path(
        'groups/<str:pk>/permissions/',
        GroupPermissionManager.as_view(),
        name='group-permissions-manage'
    ),
]

