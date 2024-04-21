import json
import os

from django.conf import settings

from recipes.models import Ingredient, Tag, User


INGREDIENTS_JSON_FILE_NAME = 'ingredients.json'
PATH_TO_INGREDIENTS_FILE = os.path.join(
    settings.INGREDIENTS_DATA_ROOT, INGREDIENTS_JSON_FILE_NAME
)


def load_data():
    with open(
        PATH_TO_INGREDIENTS_FILE, 'r', encoding="utf8"
    ) as ingredients_json:
        return json.load(ingredients_json)


INGREDIENTS = load_data()

TAGS = [
    {
        'name': 'Завтрак',
        'color': '#16f202',
        'slug': 'breakfast'
    },
    {
        'name': 'Обед',
        'color': '#fcc90f',
        'slug': 'lunch'
    },
    {
        'name': 'Ужин',
        'color': '#fc0f1f',
        'slug': 'dinner'
    },

]

USERS = [
    {
        'username': 'bestuser1',
        'first_name': 'Best',
        'last_name': 'User',
        'email': 'bestuser@yandex.ru',
        'password': 'qwerty123'
    },
    {
        'username': 'bestuser2',
        'first_name': 'Besttwo',
        'last_name': 'Usertwo',
        'email': 'bestuser2@yandex.ru',
        'password': 'qwerty123'
    },
    {
        'username': 'bestuser3',
        'first_name': 'Bestthree',
        'last_name': 'Userthree',
        'email': 'bestuser3@yandex.ru',
        'password': 'qwerty123'
    },
]

DATA_MODEL = (
    (INGREDIENTS, Ingredient),
    (TAGS, Tag),
    (USERS, User),
)
