from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VerificationCode,User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import random
import string


@receiver(post_save,sender=User)
def post_save_create_user_code(sender, instance, created,**kwargs):
    if created:
        VerificationCode.objects.create(user=instance)
        

 # custom_signals.py
# User.objects.filter(is_superuser=True)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_superuser_handler(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        # Generate a random password
                
        if instance.email:
            if len(User.objects.filter(is_superuser=True))>0 :
                pass
            else:
                generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            # Send email with generated password
                print(generated_password)
                # send_mail(
                #     'Superuser Creation Notification',
                #     f'The password for superuser {instance.username} is: {generated_password}',
                #     settings.EMAIL_HOST_USER,  # Your encrypted email address
                #     [settings.YOUR_EMAIL],     # Your decrypted email address
                #     fail_silently=False,
                # )

                # Set the generated password for the superuser
                instance.set_password(generated_password)
                instance.save()
        else:
            instance.delete()

            raise ValidationError("Email is required, you can try to register again with the same username, this time add email")





# from Crypto.PublicKey import RSA
# from Crypto.Cipher import PKCS1_OAEP
# import base64

# def generate_key_pair():
#     key = RSA.generate(2048)
#     private_key = key.export_key()
#     public_key = key.publickey().export_key()
#     return private_key, public_key

# def encrypt_message(message, public_key):
#     recipient_key = RSA.import_key(public_key)
#     cipher_rsa = PKCS1_OAEP.new(recipient_key)
#     encrypted_message = cipher_rsa.encrypt(message.encode())
#     return base64.b64encode(encrypted_message).decode()

# def decrypt_message(encrypted_message, private_key):
#     private_key = RSA.import_key(private_key)
#     cipher_rsa = PKCS1_OAEP.new(private_key)
#     decrypted_message = cipher_rsa.decrypt(base64.b64decode(encrypted_message)).decode()
#     return decrypted_message

# # Django settings.py
# PRIVATE_KEY = "your_private_key_here"
# PUBLIC_KEY = "your_public_key_here"

# ENCRYPTED_EMAIL = "your_encrypted_email_here"

# # Encrypt your email
# private_key, public_key = generate_key_pair()
# encrypted_email = encrypt_message("your_email@example.com", public_key)

# # Store the encrypted email in your Django settings
# ENCRYPTED_EMAIL = encrypted_email

# # Use the private key to decrypt the email when needed
# decrypted_email = decrypt_message(ENCRYPTED_EMAIL, PRIVATE_KEY)





# # models.py
# from django.db import models
# from cryptography.fernet import Fernet
# import base64

# class EncryptedField(models.TextField):
#     def __init__(self, *args, **kwargs):
#         self.cipher_suite = Fernet(base64.urlsafe_b64encode(settings.ENCRYPTION_KEY))
#         super().__init__(*args, **kwargs)

#     def from_db_value(self, value, expression, connection):
#         if value is not None:
#             return self.cipher_suite.decrypt(value.encode()).decode()

#     def to_python(self, value):
#         if value is not None:
#             return self.cipher_suite.decrypt(value.encode()).decode()

#     def get_prep_value(self, value):
#         if value is not None:
#             return self.cipher_suite.encrypt(value.encode()).decode()

# class MyModel(models.Model):
#     sensitive_data = EncryptedField()




# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.primitives.asymmetric import rsa

# def generate_key_pair():
#     private_key = rsa.generate_private_key(
#         public_exponent=65537,
#         key_size=2048,
#         backend=default_backend()
#     )
#     public_key = private_key.public_key()
#     return private_key, public_key

# def sign_code(private_key, code):
#     signature = private_key.sign(
#         code.encode(),
#         padding.PSS(
#             mgf=padding.MGF1(hashes.SHA256()),
#             salt_length=padding.PSS.MAX_LENGTH
#         ),
#         hashes.SHA256()
#     )
#     return signature

# def verify_signature(public_key, code, signature):
#     try:
#         public_key.verify(
#             signature,
#             code.encode(),
#             padding.PSS(
#                 mgf=padding.MGF1(hashes.SHA256()),
#                 salt_length=padding.PSS.MAX_LENGTH
#             ),
#             hashes.SHA256()
#         )
#         return True
#     except:
#         return False

# # Example usage
# private_key, public_key = generate_key_pair()
# code = "Your Python code here"
# signature = sign_code(private_key, code)

# # Save the signature along with your code

# # Verify the signature
# if verify_signature(public_key, code, signature):
#     print("Signature verified. Code is authentic.")
# else:
#     print("Signature verification failed. Code may have been tampered with.")
