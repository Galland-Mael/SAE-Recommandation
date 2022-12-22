from django import template

register = template.Library()


@register.filter(name="modulo")
def modulo(value, arg):
        return int(value) % int(arg)
