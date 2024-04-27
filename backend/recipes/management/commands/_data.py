import base64
import json
import os
import random

from django.conf import settings
from django.core.files.base import ContentFile

from recipes.models import Ingredient, Tag, User, RecipeIngredientAmount
from ._imagecode import IMAGE_CODE

INGREDIENTS_JSON_FILE_NAME = 'ingredients.json'
PATH_TO_INGREDIENTS_FILE = os.path.join(
    settings.INGREDIENTS_DATA_ROOT, INGREDIENTS_JSON_FILE_NAME
)

USER_ID_ONE = 20
USER_ID_TWO = 21
SUPERUSER_ID = 22

TAG_BREAKFAST_ID = 20
TAG_LUNCH_ID = 21
TAG_DINNER_ID = 22

TAG_LIST = [
    TAG_LUNCH_ID,
    TAG_DINNER_ID,
    TAG_BREAKFAST_ID
]

BURGER_RECIPE_ID = 20
SANDWICH_RECIPE_ID = 21
KEBAB_RECIPE_ID = 22


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
        'slug': 'breakfast',
        'id': TAG_BREAKFAST_ID
    },
    {
        'name': 'Обед',
        'color': '#fcc90f',
        'slug': 'lunch',
        'id': TAG_LUNCH_ID
    },
    {
        'name': 'Ужин',
        'color': '#fc0f1f',
        'slug': 'dinner',
        'id': TAG_DINNER_ID
    },

]

USERS = [
    {
        'username': 'bestuser1',
        'first_name': 'Best',
        'last_name': 'User',
        'email': 'bestuser@yandex.ru',
        'password': 'qwerty123',
        'id': USER_ID_ONE
    },
    {
        'username': 'bestuser2',
        'first_name': 'Besttwo',
        'last_name': 'Usertwo',
        'email': 'bestuser2@yandex.ru',
        'password': 'qwerty123',
        'id': USER_ID_TWO
    },
    {
        'username': 'superuser',
        'first_name': 'Super',
        'last_name': 'User',
        'email': 'superuser@yandex.ru',
        'password': 'superuser123',
        'id': SUPERUSER_ID,
        'is_superuser': True,
        'is_staff': True
    },
]


def get_user(user_id):
    return User.objects.get(id=user_id)


def get_tags(*args):
    return list(Tag.objects.filter(id__in=list(args)))


def get_ingredients(*args):
    return list(Ingredient.objects.filter(id__in=list(args)))


def get_image(data=IMAGE_CODE):
    if isinstance(data, str) and data.startswith('data:image'):
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]

        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

    return data


def create_ingredients_tags(recipe):
    k_tags = random.randint(1, 3)
    recipe.tags.set(
        get_tags(
            *random.choices(TAG_LIST, k=k_tags)
        )
    )
    num_range = random.randint(1, 10)
    for ingredient in get_ingredients(
        *[random.randint(1, 40) for _ in range(num_range)]
    ):
        amount = random.randint(3, 20)
        RecipeIngredientAmount.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=amount
        )


RECIPES = [
    {
        'name': 'Burger',
        'author': SUPERUSER_ID,
        'text': 'The best Burger',
        'image': get_image(),
        'id': BURGER_RECIPE_ID,
        'cooking_time': 20
    },
    {
        'name': 'Sandwich',
        'author': USER_ID_ONE,
        'text': 'The best Sandwich',
        'image': get_image(),
        'id': SANDWICH_RECIPE_ID,
        'cooking_time': 20
    },
    {
        'name': 'Kebab',
        'author': USER_ID_TWO,
        'text': 'The best Kebab',
        'image': get_image(),
        'id': KEBAB_RECIPE_ID,
        'cooking_time': 20
    },

]


TAG_INGREDIENT_DATA_MODEL = (
    (INGREDIENTS, Ingredient),
    (TAGS, Tag)
)

USER_DATA_MODEL = (
    (USERS, User),
)
