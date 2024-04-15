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
    SetPasswordSerializer,
    GetTokenSerializer
)


INCORRECT_PASSWORD = 'Неверный пароль!'
User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    # http_method_names = ('get', 'post', 'patch', 'delete',)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    # def get_permissions(self):
    #     if self.action != 'create' or self.action != 'list':
    #         self.permission_classes = [IsAuthenticated, ]
    #     else:
    #         self.permission_classes = [AllowAny, ]
    #     return super(UsersViewSet, self).get_permissions()

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_current_user_info(self, request):
        return Response(
            UsersSerializer(request.user).data,
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
