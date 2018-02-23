from django import template


register = template.Library()

@register.filter
def elements(bool, arg='PE'):
    if not bool:
        return ''
    else:
        return arg

@register.filter
def folatadd(arg1, arg2):
    return float(arg1)+float(arg2)

