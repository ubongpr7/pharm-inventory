from django.forms import ModelForm
from django.conf import settings


class UserCreateForm(ModelForm):
    class Meta:
        model= settings.AUTH_USER_MODEL

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].widgets.attrs.update({"class":"form-control"})