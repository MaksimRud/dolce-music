from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def split(word):
    return [char for char in word]

def validate_year(value):
    characters = split(value)

    first_date = "".join(characters[0:4])
    second_date = "".join(characters[5:9])
    if not first_date.isdigit() or not second_date.isdigit():
        raise ValidationError('not right year')
    else:
        first_date = int(first_date)
        second_date = int(second_date)

    if first_date >= second_date:
        raise ValidationError('not right year')
    if second_date - first_date > 500:
        raise ValidationError('not right year')
