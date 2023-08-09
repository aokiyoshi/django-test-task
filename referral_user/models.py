from django.db import models
from django.contrib.auth.models import User


class ReferralUser(User):
    firstname = models.CharField(max_length=30, default='')
    lastname = models.CharField(max_length=30, default='')
    phone_number = models.CharField(max_length=10, blank=False, unique=True)
    invite_code = models.CharField(max_length=6, unique=True) 
    referral_code = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return f'{self.pk} {self.firstname} {self.lastname} {self.phone_number}'
    

class VerifyCode(models.Model):
    code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=10, default='', unique=True)

    def __str__(self):
        return f'{self.phone_number} {self.code}'