from django.forms import ModelForm
from .models import User
from datetime import date
from django.contrib.auth.forms import UserCreationForm


YEAR_CHOICES = tuple([*range(date.today().year, date.today().year - 200, -1)])


from django import forms
from django.conf import settings


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name','last_name','username', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user



class CustomLoginForm(forms.Form):
    username = forms.CharField(required=True,)
    password = forms.CharField(widget=forms.PasswordInput,required=True)
