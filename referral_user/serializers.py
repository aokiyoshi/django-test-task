import uuid
import random
from rest_framework import serializers

from referral_user.models import ReferralUser, VerifyCode


class ReferralUserSerializer(serializers.ModelSerializer):
    """
    Общий сериализатор для пользователей
    """
    class Meta:
        model = ReferralUser
        fields = ['firstname', 'lastname', 'phone_number',
                  'invite_code', 'referral_code']

    def validate(self, attrs):
        if attrs.get('referral_code') and not ReferralUser.objects.get(invite_code=attrs['referral_code']):
            raise serializers.ValidationError('Invalid referral code')
        return super().validate(attrs)


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя
    """
    class Meta:
        model = ReferralUser
        fields = ['phone_number', 'referral_code']

    def validate(self, attrs):
        if attrs['referral_code'] and not ReferralUser.objects.get(invite_code=attrs['referral_code']):
            raise serializers.ValidationError('Invalid referral code')
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['invite_code'] = str(uuid.uuid4().hex.upper()[:6])
        validated_data['username'] = f"user_{validated_data['phone_number']}"
        VerifyCode.objects.create(
            **{'phone_number': validated_data['phone_number'], 'code': random.randint(1000, 9999)})
        return ReferralUser.objects.create(**validated_data)


class VerifyCodeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для кода верификации
    """
    class Meta:
        model = VerifyCode
        fields = ['phone_number', 'code']


class LoginUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для логина пользователя
    """
    class Meta:
        model = VerifyCode
        fields = ['phone_number', ]

    def create(self, validated_data):
        code, created = VerifyCode.objects.update_or_create(
            phone_number=validated_data.get('phone_number', None),
        defaults={'code': random.randint(1000, 9999)})
        return code


class MyReferralsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralUser
        fields = ['phone_number', 'firstname', 'lastname', 'referral_code']
