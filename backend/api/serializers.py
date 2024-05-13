from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredientAmount, Tag
from rest_framework import serializers

SAME_ID = (
    'Нельзя передавать одинаковые ID: '
    'id={id}'
)
ID_NOT_EXISTS = (
    'Объект(ы) с id = {id} не найден(ы)'
)


User = get_user_model()


class BaseUsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'is_subscribed'
        )
        read_only_fields = (
            *UserSerializer.Meta.read_only_fields,
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        request = self.context['request']
        user = request.user
        if request.auth is not None:
            return user.subscribers.all().filter(
                author=author
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountReadSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='id',
        read_only=True
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientAmount
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )
        read_only_fields = fields


class IngredientAmountCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipeToRepresentationSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountReadSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    author = BaseUsersSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, recipe):
        request = self.context['request']
        if request.auth is not None:
            return request.user.favorites.filter(
                recipe=recipe
            ).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        if request.auth is not None:
            return request.user.shoppingcarts.filter(
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

    def unique_exists_validator(self, model, ids):
        not_exists_ids = list(
            set(ids) - set(
                model.objects.filter(
                    id__in=set(ids)
                ).values_list('id', flat=True).order_by('id')
            )
        )
        not_unique_ids = list(
            set(
                [
                    id_
                    for id_ in set(ids)
                    if ids.count(id_) > 1
                ]
            )
        )
        if not_exists_ids:
            raise serializers.ValidationError(
                ID_NOT_EXISTS.format(id=not_exists_ids)
            )
        if not_unique_ids:
            raise serializers.ValidationError(
                SAME_ID.format(id=not_unique_ids)
            )

    def validate_tags(self, tags):
        self.unique_exists_validator(
            model=Tag,
            ids=self.initial_data['tags']
        )
        return tags

    def validate_ingredients(self, ingredients):
        self.unique_exists_validator(
            model=Ingredient,
            ids=[
                ingredient['id']
                for ingredient in ingredients
            ]
        )
        return ingredients

    def create(self, validated_data):
        ingredients_amount = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        RecipeIngredientAmount.objects.bulk_create(
            RecipeIngredientAmount(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient_id_amount['id']
                ),
                amount=ingredient_id_amount['amount']
            )
            for ingredient_id_amount in ingredients_amount
        )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients_amount = validated_data.pop('ingredients')
        instance.tags.set(tags)
        RecipeIngredientAmount.objects.filter(recipe=instance).delete()
        RecipeIngredientAmount.objects.bulk_create(
            RecipeIngredientAmount(
                recipe=instance,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient_id_amount['id']
                ),
                amount=ingredient_id_amount['amount']
            )
            for ingredient_id_amount in ingredients_amount
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeToRepresentationSerializer(
            instance, context=self.context
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


class SubscriptionsSerializer(BaseUsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(BaseUsersSerializer.Meta):
        fields = (
            *BaseUsersSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, user):
        recipes_limit = (
            self.context['request']
            .GET.get('recipes_limit')
        )
        if recipes_limit is not None and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
        else:
            recipes_limit = None
        return UserRecipesSerializer(
            user.recipes.all()[:recipes_limit],
            many=True
        ).data
