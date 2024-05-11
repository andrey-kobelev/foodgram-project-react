from django.core.management.base import BaseCommand

from . import _load_data
from recipes.models import Recipe


def recipes_bulk_create():
    try:
        for recip_data in _load_data.RECIPES:
            recip_data['author'] = _load_data.get_user(recip_data['author'])
            recipe = Recipe.objects.create(
                **recip_data
            )
            _load_data.create_ingredients_tags(recipe=recipe)
    except Exception as error:
        raise Exception(f'Ошибка импорта рецептов: {error}')


class Command(BaseCommand):
    help = 'This command imports recipes'

    def handle(self, *args, **options):
        try:
            print('Начало импорта рецептов...', end=' ')
            recipes_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('(ok)')
            print()
            print('Импорт рецептов выполнен успешно')
