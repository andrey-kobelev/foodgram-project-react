from datetime import datetime

from django.conf import settings
from django.db.models import Sum

from .models import RecipeIngredientAmount


SHOPPINGLIST = (
    'СПИСОК ПОКУПОК\n'
    'Дата составления списка: {date}\n'
    '=========================================\n'
    'РЕЦЕПТЫ:\n'
    '{recipes}\n\n'
    'ПРОДУКТЫ:\n'
    '{products}\n'
    '========================================='
)


def get_recipes_ids_and_names(user):
    return (
        user.shoppingcarts.select_related(
            'recipe'
        ).values('recipe__id', 'recipe__name')
    )


def get_ingredients_amount(recipes_ids: list) -> list:
    return [
        f'{num}. '
        f'{ingredient["ingredient__name"].capitalize()} '
        f'({ingredient["ingredient__measurement_unit"]}) '
        f'{ingredient["amount"]} '
        for num, ingredient in enumerate(
            (
                RecipeIngredientAmount.objects.filter(
                    recipe__in=recipes_ids
                ).values(
                    'ingredient__name',
                    'ingredient__measurement_unit'
                ).annotate(amount=Sum('amount')).order_by('ingredient')
            ),
            1
        )
    ]


def get_shoppinglist(ingredients, recipes):
    return SHOPPINGLIST.format(
        date=datetime.now().strftime(
            settings.DATE_FORMAT_FOR_SHOPPINGCART
        ),
        recipes=(
            '\n'.join([
                f' - {recipe["recipe__name"].capitalize()}'
                for recipe in recipes
            ])
        ),
        products=(
            '\n'.join(ingredients)
        )
    )
