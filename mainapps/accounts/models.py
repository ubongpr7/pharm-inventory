import os
import random
from PIL import Image
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.db.models import Q



from django.conf import settings
from django.contrib.auth.models import User,PermissionsMixin

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mainapps.company.models import Company
from mainapps.inventory.helpers.field_validators import *


PREFER_NOT_TO_SAY="not_to_mention"
SEX=(
    ("male",_("Male")),
    ("female",_("Female")),
)

class UserManager(UserManager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(username__icontains=query) | 
                         Q(first_name__icontains=query)| 
                         Q(last_name__icontains=query)| 
                         Q(email__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs

def get_upload_path(instance,filename):
    return os.path.join('images','avartar',str(instance.pk,filename))

class User(AbstractUser, PermissionsMixin):
    phone = models.CharField(
        max_length=60, 
        blank=True, 
        null=True
    )
    address = models.CharField(
        max_length=60, 
        blank=True, 
        null=True
    )
    picture = models.ImageField(
        upload_to='profile_pictures/%y/%m/%d/', 
        default='default.png', 
        null=True
    
        )
    email = models.EmailField(blank=True, null=True)
    sex=models.CharField(
        max_length=20,
        choices=SEX,
        default=PREFER_NOT_TO_SAY,
        blank=True,
        null=True
    )
    is_customer=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_main_staff=models.BooleanField(default=False)
    is_worker=models.BooleanField(default=False)
    date_of_birth = models.DateField(
        validators=[adult_validator], 
        verbose_name='Date Of Birth',
        help_text='You must be above 18 years of age.',
        blank=True,
        null=True
    )
    apt_number = models.CharField(
        max_length=200, 
        verbose_name='Apartment Number',
        help_text='Please enter your apartment number or house number.',
        blank=True,
        null=True
    )
    street_number = models.CharField(
        max_length=200, blank=True, null=True, 
        verbose_name='Street Number',
        help_text='This field is optional. Please enter your street number.',
        
    )
    street_name = models.CharField(
        verbose_name='Street Name', 
        help_text='Enter you Home Address.',
        max_length=200,
        blank=True,
        null=True,
    )
    
    city = models.CharField(
        max_length=200, validators=[alphabet_validator], 
        verbose_name='City',
        help_text='Please enter only alphabets.',
        null=True,
        blank=True,
    )
    zip_code = models.CharField(
        max_length=6, 
        validators=[zip_code_validator], 
        verbose_name='Zip Code',
        help_text='Please enter a 6 digit zip code.',
        null=True,
        blank=True,
        )
    state = models.CharField(
        max_length=200, validators=[alphabet_validator], 
        verbose_name='State',
        help_text='Please enter only alphabets.',
        null=True,
        blank=True,
   )
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='Nigeria',
    )
    
    company=models.ForeignKey(
        Company, 
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name='users'
        )
    objects = UserManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            if not self.pk:
                created_by = kwargs.pop('user', None)
                print(created_by)
                if created_by:
                    if Company.objects.get(created_by=created_by):
                        self.company=Company.objects.get(created_by=created_by)
                        self.is_worker=True
                else:
                    self.is_main_staff=True        
        except:
            pass
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
        except:
            pass
        

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_customer:
            return "Customer"
        elif self.is_staff:
            return "Staff"
        

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + 'default.png'
            return no_picture

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + 'default.png':
            self.picture.delete()
        super().delete(*args, **kwargs)


class VerificationCode(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    code=models.CharField(max_length=6,blank=True)
    slug=models.SlugField(editable=False,blank=True)
    time_requested=models.DateTimeField(auto_now=True)
    successful_attempts=models.IntegerField(default=0)
    total_attempts=models.IntegerField(default=0)
    def __str__(self):
        return self.code
    def save(self, *args,**kwargs):
        nums=[i for i in range(1,9)]
        code_list=[]
        for i in range(6):
            n=random.choice(nums)
            code_list.append(n)
        code_string="".join(str(i)  for i in code_list)
        self.code=code_string
        self.slug=self.user.username
        super().save( *args,**kwargs)
    
    class Meta:
        # extra permissions
        permissions= (
            ('code','message'),
            ('can_copy_code','Can copy code'),
            ('can_share_code','Can share code'),

        )



