import base64
import json
import os
import random

from django.conf import settings
from django.core.files.base import ContentFile

from recipes.models import Ingredient, Tag, User, RecipeIngredientAmount


INGREDIENTS_JSON_FILE_NAME = 'ingredients.json'
TAGS_JSON_FILE_NAME = 'tags.json'
IMAGE_CODE_FILE_NAME = 'image-code.txt'

PATH_TO_INGREDIENTS_FILE = os.path.join(
    settings.DATA_ROOT, INGREDIENTS_JSON_FILE_NAME
)

PATH_TO_TAGS_FILE = os.path.join(
    settings.DATA_ROOT, TAGS_JSON_FILE_NAME
)

PATH_TO_IMAGE_CODE_FILE = os.path.join(
    settings.DATA_ROOT, IMAGE_CODE_FILE_NAME
)

USER_ID_ONE = 20
USER_ID_TWO = 21
SUPERUSER_ID = 22

BURGER_RECIPE_ID = 20
SANDWICH_RECIPE_ID = 21
KEBAB_RECIPE_ID = 22


def load_data(path_to):
    with open(
        path_to, 'r', encoding="utf8"
    ) as file:
        return json.load(file)


def load_image_file():
    with open(
        PATH_TO_IMAGE_CODE_FILE, 'r', encoding="utf8"
    ) as image:
        return image.read()


INGREDIENTS = load_data(path_to=PATH_TO_INGREDIENTS_FILE)
IMAGE_CODE = load_image_file()
TAGS = load_data(path_to=PATH_TO_TAGS_FILE)

TAGS_IDS = [
    tag['id']
    for tag in TAGS
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
            *random.choices(TAGS_IDS, k=k_tags)
        )
    )
    num_ingredients = random.randint(3, 10)
    for ingredient in get_ingredients(
        *[random.randint(1, 100) for _ in range(num_ingredients)]
    ):
        RecipeIngredientAmount.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=random.randint(3, 20)
        )


RECIPES = [
    {
        'name': 'Burger',
        'author': SUPERUSER_ID,
        'text': 'The best Burger',
        'image': get_image(),
        'id': BURGER_RECIPE_ID,
        'cooking_time': 5
    },
    {
        'name': 'Sandwich',
        'author': USER_ID_ONE,
        'text': 'The best Sandwich',
        'image': get_image(),
        'id': SANDWICH_RECIPE_ID,
        'cooking_time': 11
    },
    {
        'name': 'Kebab',
        'author': USER_ID_TWO,
        'text': 'The best Kebab',
        'image': get_image(),
        'id': KEBAB_RECIPE_ID,
        'cooking_time': 45
    },

]


TAGS_DATA_MODEL = (
    (TAGS, Tag)
)
INGREDIENTS_DATA_MODEL = (
    (INGREDIENTS, Ingredient),
)
USER_DATA_MODEL = (
    (USERS, User),
)
