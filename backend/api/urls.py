from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, TagsViewSet,
                    UsersViewSet, redoc)

router = DefaultRouter()

router.register(
    prefix=r'users',
    viewset=UsersViewSet,
    basename='users'
)
router.register(
    prefix=r'tags',
    viewset=TagsViewSet,
    basename='tags'
)
router.register(
    prefix=r'ingredients',
    viewset=IngredientsViewSet,
    basename='ingredients'
)
router.register(
    prefix=r'recipes',
    viewset=RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('redoc/', redoc, name='redoc'),
    path('', include(router.urls)),
]
