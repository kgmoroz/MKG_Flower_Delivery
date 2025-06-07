from django import template

register = template.Library()

@register.filter(name="status_css")
def status_css(order):
    """Вернёт css-класс в зависимости от order.status."""
    return {
        'PENDING':    'pending',
        'PROCESSING': 'processing',
        'DELIVERING': 'delivering',
        'COMPLETED':  'completed',
    }.get(order.status, 'pending')


@register.filter
def total_price(item):
    return item.quantity * item.price


@register.filter
def sum_total(items):
    """Вернёт сумму quantity * price для коллекции OrderItem."""
    return sum(i.quantity * i.price for i in items)
