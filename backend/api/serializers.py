import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    RecipeIngredientAmount
)


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


class UsersIsSubscribedSerializer(BaseUsersSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUsersSerializer.Meta):
        model = User
        fields = BaseUsersSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, subscribing):
        request = self.context['request']
        user = request.user
        if request.auth is not None:
            return user.subscriber.all().filter(
                subscribing=subscribing
            ).exists()
        return False


class UsersSerializer(BaseUsersSerializer):

    class Meta(BaseUsersSerializer.Meta):
        model = User
        fields = BaseUsersSerializer.Meta.fields + ('password',)
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
        return BaseUsersSerializer(instance).data


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    current_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        write_only_fields = ('new_password', 'current_password')

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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient__id')
    name = serializers.CharField(source='ingredient__name')
    measurement_unit = serializers.CharField(source='ingredient__measurement_unit')
    amount = serializers.IntegerField()


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UsersIsSubscribedSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_ingredients(self, recipe):
        return IngredientAmountSerializer(
            recipe.recipe_ingredients.all().values(
                'ingredient__id',
                'ingredient__name',
                'ingredient__measurement_unit',
                'amount'
            ),
            many=True
        ).data

    def get_is_favorited(self, recipe):
        request = self.context['request']
        if request.auth is not None:
            return request.user.favorite.filter(
                recipe=recipe
            ).exists
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        if request.auth is not None:
            return request.user.shoppingcart.filter(
                recipe=recipe
            ).exists
        return False
