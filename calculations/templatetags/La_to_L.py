from django.template.defaulttags import register

@register.filter
def La_to_L(value):
    return value.replace('La', 'L')

