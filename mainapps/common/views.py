from django.shortcuts import redirect, render
from django.views.generic import CreateView,TemplateView,ListView
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.apps import apps
from django.forms import modelform_factory
# Create your views here





class HomEPage(TemplateView):
    template_name='common/home.html'


"""
####################################################################################################
Most reusable CreateView ever for non-inline_ models
"""

class AjaxTabGenericCreateView(CreateView):
    template_name = 'common/create.html'
    success_url='admin/'
    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        return apps.get_model(app_name, model_name)

    def get_form_class(self):
        return modelform_factory(self.get_model(), fields='__all__')
        


    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request:
            return JsonResponse({'success': True, 'id': self.object.id, 'name': str(self.object)})
        return response

    def form_invalid(self, form):
        if self.request:
            return JsonResponse({'success': False, 'errors': form.errors})
        
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
####################################################################################################
"""


