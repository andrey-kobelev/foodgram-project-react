from rest_framework import filters


class IngredientsSearchFilter(filters.SearchFilter):
    search_param = 'name'
