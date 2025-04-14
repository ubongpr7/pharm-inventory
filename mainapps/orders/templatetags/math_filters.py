from datetime import timedelta
from django import template

register = template.Library()

@register.filter(name='sub')
def sub(value, arg):
    return value - arg

@register.filter(name='add')
def add(value, arg):
    return value + arg


@register.filter(name='add_days')
def add_days(value, days):
    try:
        return value + timedelta(days=int(days))
    except (TypeError, ValueError):
        return value 