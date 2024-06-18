from django.core.signing import Signer
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from mainapps.management.models import CompanyProfile

signer=Signer()

def encrypt_data(data_to_be_encrypted ):
    return signer.sign(data_to_be_encrypted)

def decrypt_data(data_to_be_decrypted ):
    return signer.unsign(data_to_be_decrypted)

def management_dispatch_dispatcher(self, request):
    company_id=decrypt_data(self.kwargs['company_id'])

    try:
        self.company = get_object_or_404(CompanyProfile, unique_id=company_id)

        if hasattr(request.user,'company' ):
            if request.user.company !=self.company:
                print('thief! lol')
                if request.htmx:
                    return HttpResponse('<div id="error-message"><h2>404</h2> <h3>User does not have permission to carry out this action</h3></div>')
                return self.handle_no_permission()
        elif hasattr(self.request.user,'profile'):
            if request.user.profile != self.company:
                if request.htmx:
                    return HttpResponse('<div id="error-message" ><h2>404</h2> <h3>User does not have permission to carry out this action</h3></div>')
                return self.handle_no_permission()
        
    except Exception as e:    
        print(e)
        return self.handle_no_permission()
