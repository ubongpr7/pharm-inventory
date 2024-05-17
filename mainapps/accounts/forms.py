from django.forms import ModelForm
from .models import User
from datetime import date


YEAR_CHOICES = tuple([*range(date.today().year, date.today().year - 200, -1)])


class UserCreateForm(ModelForm):
    class Meta:
        model= User
        fields="__all__"
        # fields=('username','password')






