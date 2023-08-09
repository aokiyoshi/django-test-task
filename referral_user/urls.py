from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from referral_user.views import ListReferralUserViewSet, RegisterUser, AuthToken, ReferralUserByPhone, UserLogin, MyReferrals

from rest_framework.authtoken import views

router = routers.SimpleRouter()

router.register('ref_users', ListReferralUserViewSet)
router.register('register', RegisterUser, basename='register')
router.register('my-profile', ReferralUserByPhone, basename='my-profile')
router.register('login', UserLogin, basename='login')



urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', AuthToken.as_view()),
    path('my-profile/my-referrals', MyReferrals.as_view()),
]
