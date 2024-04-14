from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import UsersViewSet

router_v1 = SimpleRouter()

router_v1.register(
    r'users',
    UsersViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(router_v1.urls)),
]
