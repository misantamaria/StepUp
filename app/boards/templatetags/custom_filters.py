from django import template

register = template.Library()

@register.filter(name='nota_sobre_10')
def nota_sobre_10(value):
    """
    Convierte una puntuación de 0-100 a una nota sobre 10.
    Ejemplo: 75 -> 7.5
    """
    try:
        return round(float(value) / 10, 2)
    except (ValueError, TypeError):
        return 0



