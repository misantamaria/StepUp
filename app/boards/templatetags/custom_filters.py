from django import template

register = template.Library()


@register.filter(name='nota_sobre_10')
def nota_sobre_10(porcentaje):
    """Convierte un porcentaje (0-100) a nota sobre 10"""
    if porcentaje is None:
        return 0
    try:
        nota = float(porcentaje) / 10
        return round(nota, 1)
    except (ValueError, TypeError):
        return 0
