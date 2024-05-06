from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


def get_recipes(recipes, request, user_related_objects, value):
    if request.auth is None or not value:
        return recipes.objects.none()
    return recipes.objects.filter(
        id__in=[
            id_[0] for id_ in (
                user_related_objects
                .select_related('recipe')
                .values_list('recipe__id')
            )
        ]
    )


class IngredientsSearchFilter(SearchFilter):
    search_param = 'name'


class RecipesFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='favorites'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def favorites(self, recipes, name, value):
        return get_recipes(
            recipes=recipes,
            request=self.request,
            user_related_objects=self.request.user.favorites,
            value=value
        )

    def shopping_cart(self, recipes, name, value):
        return get_recipes(
            recipes=recipes,
            request=self.request,
            user_related_objects=self.request.user.shoppingcart,
            value=value
        )
