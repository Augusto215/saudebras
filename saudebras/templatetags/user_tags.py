from django import template
register = template.Library()

@register.filter
def is_instance_of(value, class_str):
    return isinstance(value, eval(class_str))