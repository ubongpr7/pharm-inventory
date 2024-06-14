from django.db import transaction
from django.shortcuts import redirect, render
from django.views.generic import CreateView,TemplateView,ListView
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.apps import apps
from django.forms import modelform_factory
# Create your views here
from cities_light.models import Region, City,SubRegion

from mainapps.inventory.crud_logic import inventory_creation_logic
from mainapps.inventory.forms import InventoryCategoryForm
from mainapps.management.security.encripters import management_dispatch_dispatcher
from django.contrib.auth.mixins import LoginRequiredMixin





class HomEPage(TemplateView):
    # template_name='common/home.html'
    template_name='dashboard/index.html'


"""
#############Most reusable CreateView ever for non-inline_ models#######################################################################################

"""

class AjaxTabGenericCreateView(LoginRequiredMixin,CreateView):
    template_name = 'common/create.html'
    success_url='/'
    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        return apps.get_model(app_name, model_name)

    def get_form_class(self):
        if self.kwargs['model_name'] == 'inventorycategory':
            return InventoryCategoryForm
        return modelform_factory(self.get_model(), fields='__all__')
        


    def dispatch(self, request, *args, **kwargs):
        management_dispatch_dispatcher(self=self,request=request)
        
        if not request.user.has_perm(f'{self.kwargs['app_name']}.add_{self.kwargs['model_name']}'): 
            print('no permission')  
            print(self.request.user) 
            # print(request.user.user_permissions.objects.all()) 
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
                
            if hasattr(self.get_model(),'profile'):
                if self.request.user.company:
                    form.instance.profile= self.request.user.company
                elif self.request.user.profile:
                    form.instance.profile= self.request.user.profile
            if hasattr(self.get_model(),'created_by'):
                form.instance.created_by = self.request.user
            # if self.kwargs['app_name'] == 'inventory':
            #     inventory_creation_logic(self,form)    
            response = super().form_valid(form)
            
            return response

    def form_invalid(self, form):
        
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs ) :
        context= super().get_context_data(**kwargs)
        context['form']=self.get_form()
    
    
        try:

            context['item_name'] = self.get_model()._meta.verbose_name.title()
        except Exception as error:
            context['item_name'] = self.get_model().__name__

            print(self.get_model().__name__ ,error)    

        try:

            context['plural'] = self.get_model()._meta.verbose_name_plural.title
        except Exception as error:
            print(self.get_model().__name__ ,error)    
        context['ajax_url'] = f'/add/{self.kwargs['app_name']}/{self.kwargs['model_name']}/' 
        context['get_url'] = f'/list/{self.kwargs['app_name']}/{self.kwargs['model_name']}/' 
        context['done_url'] = self.success_url
        return context







class AjaxGenericList(ListView):
    paginate_by = 3  
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        context['page_obj'] = context['paginator'].get_page(page)
    

        return context
    def dispatch(self, request, *args, **kwargs):
        management_dispatch_dispatcher(self=self,request=request)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        model = self.get_model()
        return model.objects.all()

    
    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        return apps.get_model(app_name, model_name)
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.method == 'GET':
            items = list(context['items'].values())
            return JsonResponse({
                'items': items,
                'pagination': {
                    'current_page': context['page_obj'].number,
                    'total_pages': context['paginator'].num_pages,
                    'has_previous': context['page_obj'].has_previous(),
                    'has_next': context['page_obj'].has_next(),
                }
            })
        return super().render_to_response(context, **response_kwargs)


"""
##############################################Location deals ######################################################
"""

def get_regions(request):
    country_id = request.GET.get('addresses-0-country')
    regions = Region.objects.filter(country_id=country_id)
    return render(request,'common/address/regions.html',{'regions':regions})

def get_subregions(request):
    region_id = request.GET.get('addresses-0-region')
    # subregions = SubRegion.objects.all()
    subregions = SubRegion.objects.filter(region_id=region_id)
    return render(request,'common/address/subregions.html',{'subregions':subregions})

def get_cities(request):
    subregion_id = request.GET.get('addresses-0-subregion')
    cities = City.objects.filter(subregion_id=subregion_id).values('id', 'name')
    return render(request,'common/address/cities.html',{'cities':cities})


"""
####################################################################################################
"""



