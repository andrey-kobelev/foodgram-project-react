from django.core.management.base import BaseCommand

from ._data import DATA_MODEL, RECIPES, create_ingredients_tags, get_user
from recipes.models import Recipe


def users_tags_ingredients_bulk_create():
    try:
        for datas, model in DATA_MODEL:
            model.objects.bulk_create(
                model(**data)
                for data in datas
            )
    except Exception as error:
        print(
            f'Произошла ошибка при создании объектов:'
            f'{error}'
        )


def recipes_bulk_create():
    try:
        for recip_data in RECIPES:
            recip_data['author'] = get_user(recip_data['author'])
            recipe = Recipe.objects.create(
                **recip_data
            )
            create_ingredients_tags(recipe=recipe)
    except Exception as error:
        print(f'Ошибка при создании рецептов: {error}')


class Command(BaseCommand):
    help = 'This command populates the database'

    def handle(self, *args, **options):
        try:
            print('START!')
            users_tags_ingredients_bulk_create()
            recipes_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('FINISH!')
