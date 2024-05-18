from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from . import serializers as api_serializers
from .filters import IngredientsSearchFilter, RecipesFilter
from .paginators import LimitPageQueryParamsPaginator
from .permissions import AuthorSafeMethods
from recipes import models as recipes_models
from recipes import utils

SUBSCRIPTION_ERROR = 'Вы уже подписаны на пользователя {name}'
FAVORITE_ERROR = 'Рецепт {name} уже есть в избранном'
SHOPPING_CART_ERROR = 'Рецепт {name} уже есть в списке покупок'

User = get_user_model()


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageQueryParamsPaginator

    def get_permissions(self):
        if self.action == 'me':
            if self.request.method != 'GET':
                raise PermissionDenied()
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
        url_name='subscribe'
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise ValidationError(
                'Вы не можете подписаться сами на себя!'
            )
        if request.method == 'POST':
            subscription, created = (
                recipes_models.Subscriptions.objects.get_or_create(
                    user=user, author=author
                )
            )
            if not created:
                raise ValidationError(
                    SUBSCRIPTION_ERROR.format(
                        name=subscription.author.username
                    )
                )
            serializer = api_serializers.SubscriptionsSerializer(
                author, context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        get_object_or_404(
            user.subscribers.all(), author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            authors__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = api_serializers.SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(
            serializer.data
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = recipes_models.Tag.objects.all()
    serializer_class = api_serializers.TagSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = recipes_models.Ingredient.objects.all()
    serializer_class = api_serializers.IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientsSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = recipes_models.Recipe.objects.all()
    serializer_class = api_serializers.RecipeSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AuthorSafeMethods
    )
    pagination_class = LimitPageQueryParamsPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    filterset_fields = ('tags', 'author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def shopping_cart_or_favorites(
            self,
            pk,
            request,
            object_,
            error,
            user_related_objects
    ):
        recipe = get_object_or_404(recipes_models.Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            obj, created = object_.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if not created:
                raise ValidationError(
                    error.format(
                        name=recipe.name
                    )
                )
            return Response(
                api_serializers.UserRecipesSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(user_related_objects, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(AuthorSafeMethods,),
        url_path='favorite',
        url_name='favorite'
    )
    def favorite(self, request, pk=None):
        return self.shopping_cart_or_favorites(
            pk=pk,
            request=request,
            object_=recipes_models.Favorite,
            error=FAVORITE_ERROR,
            user_related_objects=request.user.favorites.all()
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(AuthorSafeMethods,),
        url_path='shopping_cart',
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        return self.shopping_cart_or_favorites(
            pk=pk,
            request=request,
            object_=recipes_models.ShoppingCart,
            error=SHOPPING_CART_ERROR,
            user_related_objects=request.user.shoppingcarts.all()
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(AuthorSafeMethods,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        recipes_names_ids = utils.get_recipes_ids_and_names(user=request.user)
        ingredients_amount = utils.get_ingredients_amount(
            recipes_ids=[
                recipe['recipe__id']
                for recipe in recipes_names_ids
            ],
        )
        return FileResponse(
            utils.get_shoppinglist(
                ingredients=ingredients_amount,
                recipes=recipes_names_ids
            ),
            content_type='text/plain; charset=utf-8'
        )
