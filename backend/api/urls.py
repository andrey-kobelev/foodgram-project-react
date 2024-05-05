from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, TagsViewSet,
                    UsersViewSet)

router_v1 = DefaultRouter()

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

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
