import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django_extensions.validators import HexValidator

BAD_USERNAME = (
    'Неверный формат имени. '
    'Запрещенные символы: {characters}'
)
BAD_HEX_COLOR = 'Неверный формат hex color: {hex}'


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


class HexColorValidator(HexValidator):
    def __call__(self, value):
        hex_color = str(value)
        if not hex_color.startswith('#'):
            raise ValidationError(
                BAD_HEX_COLOR.format(
                    hex=hex_color
                )
            )
        super().__call__(hex_color.replace('#', ''))
