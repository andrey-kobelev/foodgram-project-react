from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from django.db.models import Q

from recipes.models import Recipe, Tag


class IngredientsSearchFilter(SearchFilter):
    search_param = 'name'


class RecipesFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_recipes'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_recipes'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author'
        )

    def get_recipes(self, recipes, name, value):
        if self.request.auth is None or not value:
            return recipes.objects.none()
        user = self.request.user
        related_filter = Q(shoppingcarts__user=user)
        if name == 'is_favorited':
            related_filter = Q(favorites__user=user)
        return recipes.filter(related_filter)
