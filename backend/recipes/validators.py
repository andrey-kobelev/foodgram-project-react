import re

from django.conf import settings
from django.core.exceptions import ValidationError

BAD_USERNAME = (
    'Неверный формат имени. '
    'Запрещенные символы: {characters}'
)
BAD_HEX_COLOR = 'Неверный формат hex color: {hex}. Error: {error}'


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
    try:
        if (
            not hex_color.startswith('#')
            or len(hex_color.split('#')[1]) != settings.HEX_COLOR_LENGTH
        ):
            raise ValueError()
        int(hex_color.split('#')[1], 16)
        return hex_color
    except ValueError as error:
        raise ValidationError(
            BAD_HEX_COLOR.format(
                hex=hex_color, error=error
            )
        )
