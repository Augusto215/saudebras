from django import template
from math import floor as math_floor

register = template.Library()

@register.filter
def floor(value):
    return math_floor(value)

@register.filter
def absolute(value):  # mudar o nome para evitar a recursão
    return abs(value)

@register.filter
def mul(value, arg):
    return value * arg
