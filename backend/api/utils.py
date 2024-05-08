
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
        .annotate(amount=aggregate_sum('amount'))
        .order_by('ingredient')
    )
