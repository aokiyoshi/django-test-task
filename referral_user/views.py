
from typing import Any
from rest_framework import mixins, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from referral_user.models import ReferralUser, VerifyCode
from referral_user.serializers import (LoginUserSerializer, ReferralUserSerializer,
                                       RegisterUserSerializer, VerifyCodeSerializer, MyReferralsSerializer)

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, schema


class ListReferralUserViewSet(ModelViewSet):
    """
    Методы для работы с пользователями
    """
    queryset = ReferralUser.objects.all()
    serializer_class = ReferralUserSerializer


class RegisterUser(mixins.CreateModelMixin, GenericViewSet):
    """
    Метод для регистрации пользователя
    """
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = RegisterUserSerializer()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthToken(ObtainAuthToken):
    """
    Метод для получения токена
    """
    serializer_class = VerifyCodeSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        ver_code = VerifyCode.objects.get(
            phone_number=data['phone_number'], code=data['code'])
        if not ver_code:
            return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        user = ReferralUser.objects.get(phone_number=data['phone_number'])
        token, created = Token.objects.get_or_create(user=user)
        ver_code.delete()
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'phone_number': user.phone_number
        })


class ReferralUserByPhone(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """
    Метод для получения профиля пользователя по номеру телефона
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]
    lookup_field = 'phone_number'
    queryset = ReferralUser.objects.all()
    serializer_class = ReferralUserSerializer

    def get_queryset(self):
        user = ReferralUser.objects.get(
            phone_number=self.kwargs['phone_number'])
        token = self.request.META.get('HTTP_AUTHORIZATION', None)
        stored_token = Token.objects.get(user=user)
        if not stored_token:
            return None
        if str(token) != str(stored_token):
            return None
        return super().get_queryset().filter(phone_number=self.kwargs['phone_number'])


class UserLogin(mixins.CreateModelMixin, GenericViewSet):
    """
    Метод для аутентификации по номеру телефона
    """
    serializer_class = LoginUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        phone = request.data.get('phone_number', None)
        ver_code = None
        try:
            ver_code = VerifyCode.objects.get(phone_number=phone)
        except VerifyCode.DoesNotExist:
            pass
        if ver_code:
            return Response(dict(**request.data, code=ver_code.code), status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            ver_code = VerifyCode.objects.get(
                phone_number=serializer.data['phone_number'])
            return Response(dict(**serializer.data, code=ver_code.code), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyReferrals(generics.ListAPIView):
    """
    Методы для работы с пользователями
    """
    queryset = ReferralUser.objects.all()
    serializer_class = MyReferralsSerializer

    def get_queryset(self):
        token = str(self.request.META.get('HTTP_AUTHORIZATION', None))
        user = ReferralUser.objects.get(
            username=Token.objects.get(key=token).user.username)
        referrals = super().get_queryset().filter(referral_code=user.invite_code)
        if not referrals:
            return []
        return referrals
