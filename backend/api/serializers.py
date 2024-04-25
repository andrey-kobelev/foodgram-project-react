import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
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


class IngredientAmountReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient__id')
    name = serializers.CharField(source='ingredient__name')
    measurement_unit = serializers.CharField(source='ingredient__measurement_unit')
    amount = serializers.IntegerField()


class IngredientAmountCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipeToRepresentationSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UsersIsSubscribedSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_ingredients(self, recipe):
        return IngredientAmountReadSerializer(
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
            ).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        if request.auth is not None:
            return request.user.shoppingcart.filter(
                recipe=recipe
            ).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = IngredientAmountCreateSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
            'tags',
            'author'
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients_amount = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        tags_list = []
        for tag in tags:
            tags_list.append(tag)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_list)
        for ingredient_id_amount in ingredients_amount:
            ingredient_id = ingredient_id_amount['id']
            amount = ingredient_id_amount['amount']
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            RecipeIngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        tags_list = []
        for tag in tags:
            tags_list.append(tag)
        instance.tags.set(tags_list)
        RecipeIngredientAmount.objects.filter(recipe=instance).delete()
        for ingredient_amount in ingredients_data:
            ingredient_id = ingredient_amount['id']
            amount = ingredient_amount['amount']
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            RecipeIngredientAmount.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeToRepresentationSerializer(
            instance, context={'request': self.context['request']}
        ).data


class UserRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionsSerializer(UsersIsSubscribedSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersIsSubscribedSerializer.Meta):
        fields = UsersIsSubscribedSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )
        read_only_fields = fields

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_recipes(self, user):
        recipes_limit = (
            self.context['request']
            .query_params.get('recipes_limit', None)
        )
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
        recipes = user.recipes.all()[:recipes_limit]
        return UserRecipesSerializer(
            recipes,
            many=True
        ).data

