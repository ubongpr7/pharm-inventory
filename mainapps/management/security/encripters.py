from django.core.signing import Signer
from django.shortcuts import get_object_or_404

from mainapps.management.models import CompanyProfile

signer=Signer()

def encrypt_data(data_to_be_encrypted ):
    return signer.sign(data_to_be_encrypted)

def decrypt_data(data_to_be_decrypted ):
    return signer.unsign(data_to_be_decrypted)

def management_dispatch_dispatcher(self, request):
    company_id=decrypt_data(self.kwargs['company_id'])

    self.company = get_object_or_404(CompanyProfile, unique_id=company_id)
    try:

        if hasattr(request.user,'company' ):
            if request.user.company !=self.company:
                print('thief! lol')
                return self.handle_no_permission()
        elif hasattr(self.request.user,'profile'):
            if request.user.profile != self.company:
                return self.handle_no_permission()
        
    except Exception as e:    
        print(e)
        return self.handle_no_permission()
