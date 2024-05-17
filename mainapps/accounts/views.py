from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
from django.views import generic
from django.contrib import messages
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from mainapps.accounts.forms import UserCreateForm
from mainapps.email_system.emails import send_html_email


from .models import User,VerificationCode
    


class CreateUser(generic.CreateView):
    form_class = UserCreateForm
    template_name='accounts/create.html'
    model=User
    success_url= _('accounts/verify')
class LoginUser(generic.View):
    form_class = 'LoginUserForm'
    template_name='accounts/login.html'
    
    def get(self,request):
        form =self.form_class
        return render(request,self.template_name, {"form":form})
    
    def post(self,request):
        if request.method== "POST":
            form = "LoginUserForm(request, data=request.POST)"


        
def send_code(request):
    pk =request.session.get('pk')
    verified=request.session.get("verified ")

    if pk:
        user= User.objects.get(pk=pk)
        code =VerificationCode.objects.get(slug=user.username)
        code.total_attempts+=1
        code.save()
        code =VerificationCode.objects.get(slug=user.username)
        print(code)
        messages.success(request,'Code sent')
        return redirect('/verification')
    else:
        messages.error(request,'Session expired')
        return redirect('/signin')
    return redirect('/account/verification')



def twofa(request):
    title="Authentications"
    pk=request.session.get('pk')
    verified=request.session.get("verified ")

    if verified:  
        return redirect("/")
    else:
        if pk:
            print(f'pk: {pk}')
            user =User.objects.get(pk=pk)
            html_file='verify.html'
            to_email=user.email
            from_email= settings.EMAIL_HOST_USER
            code=VerificationCode.objects.get(slug=user.email)
            code.total_attempts+=1
            code.save()
            code =VerificationCode.objects.get(slug=user.username)
            
            print(f'this is the code: {code}')
            subject=f'Verification code: {code}. {user.first_name} {user.last_name}'
            message= code
            
            
            if request.method!="POST":
            
                
                send_html_email(subject, message, from_email, to_email,html_file)
            if request.method=="POST":
                
                num=request.POST.get('code')
                print(num)
                
                if str(code)==num:
                    code.successful_attempts+=1
                    code.save()
                    login(request, user)
                    messages.success(request,"Authentication Successful!")
                    request.session["verified "]=True
                    
                    return redirect('/')
                else :
                    messages.error(request,"You have entered an invalid code and therefore need to restart Authentication for security reasons")
                    return redirect('/account/signin')
    return render(request,"twofa.html",{'title':title})

def get_verification(request):
    pass 

