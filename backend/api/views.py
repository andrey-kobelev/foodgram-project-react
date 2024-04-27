from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from subscriptions.models import Subscriptions

from .filters import IngredientsSearchFilter
from .paginators import UsersPaginator
from .permissions import AdminAuthorSafeMethods, AdminUserSafeMethodsOrCreate
from .serializers import (GetTokenSerializer, IngredientSerializer,
                          RecipeSerializer, SetPasswordSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserRecipesSerializer, UsersIsSubscribedSerializer,
                          UsersSerializer)

INCORRECT_PASSWORD = 'Неверный пароль!'
SUBSCRIPTION_ERROR = 'Вы уже подписаны на пользователя {name}'
FAVORITE_ERROR = 'Рецепт {name} уже есть в избранном'
SHOPPING_CART_ERROR = 'Рецепт {name} уже есть в списке покупок'

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UsersPaginator
    http_method_names = ('get', 'post', 'delete')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UsersIsSubscribedSerializer
        return UsersSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly,
                                  AdminUserSafeMethodsOrCreate]
        return [permission() for permission in permission_classes]

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_current_user_info(self, request):
        return Response(
            UsersIsSubscribedSerializer(
                request.user, context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=['POST'],
        detail=False,
        url_path='set_password',
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
        url_name='subscribe'
    )
    def subscribe(self, request, pk=None):
        user = request.user
        subscribing_user = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            subscription, created = Subscriptions.objects.get_or_create(
                user=user,
                subscribing=subscribing_user
            )
            if user == subscribing_user:
                raise ValidationError(
                    'Вы не можете подписаться сами на себя!'
                )
            if not created:
                raise ValidationError(
                    SUBSCRIPTION_ERROR.format(
                        name=subscription.subscribing.username
                    )
                )
            serializer = SubscriptionsSerializer(
                subscribing_user, context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        get_object_or_404(
            user.subscriber.all(), subscribing=subscribing_user
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
            obj.subscribing
            for obj in request.user.subscriber.select_related('subscribing')
        )
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(
                serializer.data
            )
        serializer = SubscriptionsSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['POST'])
@permission_classes((AllowAny,))
def token_login(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = get_object_or_404(User, email=data['email'])
    if not user.check_password(data['password']):
        raise ValidationError(INCORRECT_PASSWORD)
    token, created = Token.objects.get_or_create(user=user)
    return Response(
        data={'auth_token': token.key}, status=status.HTTP_200_OK
    )


@api_view(http_method_names=['POST'])
@permission_classes(permission_classes=[IsAuthenticated])
def token_logout(request):
    user = request.user
    token = Token.objects.get(user=user)
    token.delete()
    return Response(
        status=status.HTTP_204_NO_CONTENT
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
    pagination_class = UsersPaginator

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
