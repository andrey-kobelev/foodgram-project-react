import re

from django.conf import settings
from django.core.exceptions import ValidationError

BAD_USERNAME = (
    'Неверный формат имени. '
    'Запрещенные символы: {characters}'
)


def username_validator(username):
    bad_characters = re.sub(
        settings.USERNAME_PATTERN, '', username
    )
    if bad_characters:
        raise ValidationError(
            BAD_USERNAME.format(
                characters=''.join(set(bad_characters))
            )
        )
    return username


def hex_color_validator(hex_color):
    pass
