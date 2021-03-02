import math
from django import template

register = template.Library()


@register.filter(name='round_less')
def round_to_less(value: float):
    """ rounds 43.5987 to 43"""
    return math.floor(value)


@register.filter(name='string_to_int')
def string_to_int(value: str):
    return int(value)


