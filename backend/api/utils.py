from datetime import datetime

from django.conf import settings

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
    return tuple(
        user.shoppingcart
        .select_related('recipe')
        .values('recipe__id', 'recipe__name')
    )


def get_ingredients_amount(recipes, aggregator_sum, obj):
    return tuple(
        obj
        .objects
        .filter(
            recipe__in=[
                recipe_id['recipe__id']
                for recipe_id in recipes
            ]
        )
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(amount=aggregator_sum('amount'))
        .order_by('ingredient')
    )


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
            '\n'.join([
                f'{num}. '
                f'{ingredient["ingredient__name"].capitalize()} '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
                for num, ingredient in enumerate(ingredients, 1)
            ])
        )
    )


def get_shop_file(response_class, shopping_list):
    response = response_class(
        shopping_list,
        content_type='text/plain'
    )
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(
            settings.SHOPPINGLIST_FILE_NAME
        )
    )
    return response
