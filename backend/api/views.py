from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import (
    UsersSerializer,
    UsersIsSubscribedSerializer,
    SetPasswordSerializer,
    GetTokenSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionsSerializer,
    UserRecipesSerializer
)
from subscriptions.models import Subscriptions
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart
)


INCORRECT_PASSWORD = 'Неверный пароль!'
SUBSCRIPTION_ERROR = 'Вы уже подписаны на пользователя {name}'
FAVORITE_ERROR = 'Рецепт {name} уже есть в избранном'
SHOPPING_CART_ERROR = 'Рецепт {name} уже есть в списке покупок'

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'delete')
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UsersIsSubscribedSerializer
        return UsersSerializer

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
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['current_password'])
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
            for obj in request.user.subscriber.all()
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
    permission_classes(AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes(AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes(AllowAny,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(AllowAny,),
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
        permission_classes=(AllowAny,),
        url_path='shopping_cart',
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            favorite, created = ShoppingCart.objects.get_or_create(
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
        permission_classes=(AllowAny,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)
