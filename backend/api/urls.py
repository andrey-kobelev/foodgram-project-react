from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import UsersViewSet, token_login, token_logout

router_v1 = SimpleRouter()

router_v1.register(
    r'users',
    UsersViewSet,
    basename='users'
)

auth_urls = ([
    path('login/', token_login, name='token_login'),
    path('logout/', token_logout, name='token_logout'),
], 'auth')

urlpatterns = [
    path('auth/token/', include(auth_urls)),
    path('', include(router_v1.urls)),
]
