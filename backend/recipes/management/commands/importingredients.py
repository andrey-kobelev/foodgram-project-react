import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


INGREDIENTS_JSON_FILE_NAME = 'ingredients.json'
PATH_TO_INGREDIENTS_FILE = os.path.join(
    settings.INGREDIENTS_DATA_ROOT, INGREDIENTS_JSON_FILE_NAME
)


def load_data():
    with open(
        PATH_TO_INGREDIENTS_FILE, 'r', encoding="utf8"
    ) as ingredients_json:
        return json.load(ingredients_json)


def ingredients_bulk_create():
    try:
        Ingredient.objects.bulk_create(
            Ingredient(**data)
            for data in load_data()
        )
    except Exception as error:
        print(
            f'Произошла ошибка при создании объектов модели Ingredient: '
            f'{error}'
        )


class Command(BaseCommand):
    help = 'This command populates the database'

    def handle(self, *args, **options):
        try:
            print('START!')
            ingredients_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('FINISH!')
