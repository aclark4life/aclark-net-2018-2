from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """
    """
    return float(value) * float(arg.total_seconds() / 60)
