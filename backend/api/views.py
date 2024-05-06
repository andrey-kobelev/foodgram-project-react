from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from recipes.models import (Favorite, Ingredient,
                            Recipe, ShoppingCart, Tag, Subscriptions)
from .filters import IngredientsSearchFilter, RecipesFilter
from .paginators import LimitPageQueryParamsPaginator
from .permissions import AdminAuthorSafeMethods
from .serializers import (IngredientSerializer,
                          RecipeSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserRecipesSerializer, UsersIsSubscribedSerializer, )

INCORRECT_PASSWORD = 'Неверный пароль!'
SUBSCRIPTION_ERROR = 'Вы уже подписаны на пользователя {name}'
FAVORITE_ERROR = 'Рецепт {name} уже есть в избранном'
SHOPPING_CART_ERROR = 'Рецепт {name} уже есть в списке покупок'

User = get_user_model()


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageQueryParamsPaginator

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'list']:
            return (AllowAny(),)
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
            subscription, created = Subscriptions.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                raise ValidationError(
                    SUBSCRIPTION_ERROR.format(
                        name=subscription.author.username
                    )
                )
            serializer = SubscriptionsSerializer(
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
        subscriptions = tuple(
            obj.author
            for obj in request.user.subscribers.select_related('author')
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(
            serializer.data
        )


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientsSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AdminAuthorSafeMethods
    )
    pagination_class = LimitPageQueryParamsPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    filterset_fields = ('tags', 'author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(AdminAuthorSafeMethods,),
        url_path='favorite',
        url_name='favorite'
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if not created:
                raise ValidationError(
                    FAVORITE_ERROR.format(
                        name=recipe.name
                    )
                )
            return Response(
                UserRecipesSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(user.favorite.all(), recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(AdminAuthorSafeMethods,),
        url_path='shopping_cart',
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            shopping_obj, created = ShoppingCart.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if not created:
                raise ValidationError(
                    SHOPPING_CART_ERROR.format(
                        name=recipe.name
                    )
                )
            return Response(
                UserRecipesSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(user.shoppingcart.all(), recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(AdminAuthorSafeMethods,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping = dict()
        recip_names = []
        shopping_cart = user.shoppingcart.select_related('recipe')
        for recipe_from_shopping_cart in shopping_cart:
            recip_names.append(
                f' - «{recipe_from_shopping_cart.recipe.name}»'.title()
            )
            ingredients = (
                recipe_from_shopping_cart
                .recipe.recipe_ingredients
                .select_related('ingredient')
                .values_list(
                    'ingredient__name',
                    'ingredient__measurement_unit',
                    'amount'
                )
            )
            for name, measurement_unit, amount in ingredients:
                ingredient = (name, measurement_unit)
                if ingredient not in shopping:
                    shopping[ingredient] = amount
                else:
                    shopping[ingredient] += amount
        shopping_list = ('СПИСОК ПОКУПОК ДЛЯ: \n{recipes}'
                         '\n_________________________________\n')
        for ingredient, amount in shopping.items():
            name, measurement_unit = ingredient
            shopping_list += (f'{name.lower()}: {amount:,d} '
                              f'{measurement_unit}\n')
        filename = "shoplist.txt"
        content = shopping_list.format(recipes='\n'.join(recip_names))
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response
