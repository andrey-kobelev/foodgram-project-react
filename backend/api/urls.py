from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientsViewSet, RecipeViewSet, TagsViewSet,
                    UsersViewSet, token_login, token_logout)

router_v1 = SimpleRouter()

router_v1.register(
    prefix=r'users',
    viewset=UsersViewSet,
    basename='users'
)
router_v1.register(
    prefix=r'tags',
    viewset=TagsViewSet,
    basename='tags'
)
router_v1.register(
    prefix=r'ingredients',
    viewset=IngredientsViewSet,
    basename='ingredients'
)
router_v1.register(
    prefix=r'recipes',
    viewset=RecipeViewSet,
    basename='recipes'
)

auth_urls = ([
    path('login/', token_login, name='token_login'),
    path('logout/', token_logout, name='token_logout'),
], 'auth')

urlpatterns = [
    path('auth/token/', include(auth_urls)),
    path('', include(router_v1.urls)),
]
