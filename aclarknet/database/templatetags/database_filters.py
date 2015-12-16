from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """
    """

    if not value:
        return 0.00

    return float(value) * float(arg.total_seconds() / 60)
