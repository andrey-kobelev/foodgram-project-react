from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

from subscriptions.models import Subscriptions


PASSWORD_MISMATCH = (
    'Пожалуйста, убедитесь, что ваш пароль совпадает!'
)


User = get_user_model()


class UsersWithoutPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
        )
        read_only_fields = fields


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'password'
        )
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, users):
        return UsersWithoutPasswordSerializer(users).data


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
    current_password = serializers.CharField(
        required=True, validators=[validate_password]
    )

    def validate(self, data):
        if data['current_password'] != data['new_password']:
            raise serializers.ValidationError(
                PASSWORD_MISMATCH
            )
        return data


class GetTokenSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True, write_only=True
    )
    email = serializers.EmailField(
        required=True, validators=[validate_email]
    )


class SubscriptionsSerializer(serializers.ModelSerializer):
    subscribing = UsersWithoutPasswordSerializer(read_only=True)

    class Meta:
        model = Subscriptions
        fields = ('subscribing',)
