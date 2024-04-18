from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email


PASSWORD_MISMATCH = (
    'Пожалуйста, убедитесь, что ваш пароль совпадает!'
)


User = get_user_model()


class BaseUsersSerializer(serializers.ModelSerializer):

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


class IsSubscribedSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        request = self.context['request']
        data = BaseUsersSerializer(instance).data
        user = request.user
        data['is_subscribed'] = False
        if request.method == 'GET' and request.auth is not None:
            is_subscribed = user.subscriber.all().filter(
                subscribing=instance
            ).exists()
            data['is_subscribed'] = is_subscribed
        return data


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'password',
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

    def to_representation(self, instance):
        request = self.context['request']
        return IsSubscribedSerializer(
            instance, context={'request': request}
        ).data


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
