from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UsersSerializer


User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    # permission_classes = (AdminOnly,)
    # pagination_class = PageNumberPagination
    # http_method_names = ('get', 'post', 'patch', 'delete',)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
        # permission_classes=(IsAuthenticated,)
    )
    def get_current_user_info(self, request):
        return Response(
            UsersSerializer(request.user).data,
            status=status.HTTP_200_OK
        )
