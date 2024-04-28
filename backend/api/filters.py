from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

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
        method='favorites'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def favorites(self, queryset, name, value):
        request = self.request
        if request.auth is None or not value:
            return Recipe.objects.none()
        favorite = (
            request.user
            .favorite
            .select_related('recipe')
            .values_list('recipe__id')
        )
        return Recipe.objects.filter(id__in=[id_[0] for id_ in favorite])

    def shopping_cart(self, queryset, name, value):
        request = self.request
        if request.auth is None or not value:
            return Recipe.objects.none()
        shopping = (
            request.user
            .shoppingcart
            .select_related('recipe')
            .values_list('recipe__id')
        )
        return Recipe.objects.filter(id__in=[id_[0] for id_ in shopping])
