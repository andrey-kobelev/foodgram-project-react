from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredientAmount, ShoppingCart


class RecipeIngredientAmountInLine(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorites_counter'
    )

    def favorites_counter(self, instance):
        return str(instance.favorites_counter())

    inlines = (RecipeIngredientAmountInLine,)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'
