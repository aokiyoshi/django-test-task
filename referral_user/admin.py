from django.contrib import admin

from referral_user.models import ReferralUser, VerifyCode

# Register your models here.
admin.site.register(ReferralUser)
admin.site.register(VerifyCode)