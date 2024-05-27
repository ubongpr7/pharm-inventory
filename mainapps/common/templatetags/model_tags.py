from django import template
from django.apps import apps


register= template.Library()

@register.inclusion_tag('wrapper/tags/model_list.html')
def model_list():
    apps_list=[]
    excluded_apps=['admin','auth','contenttypes','accounts','common','sessions','messages','staticfiles','content_type_linking_models','permit','widget_tweaks','bootstrap5']
    for app in apps.get_app_configs():
        if app.label not in excluded_apps:
        
            models_list=[]

            for model in app.get_models():
                models_list.append(model.__name__)

            apps_list.append((app.label.title(),models_list))    
    return {'apps_list': apps_list}    


@register.inclusion_tag('wrapper/tags/settings.html')
def settings():
    apps_list=[]
    excluded_apps=['accounts','permit','permissions']
    for app in apps.get_app_configs():
        if app.label  in excluded_apps:
        
            models_list=[]

            for model in app.get_models():
                models_list.append(model.__name__)

            apps_list.append((app.label.title(),models_list))    
    return {'settings_apps': apps_list}    

