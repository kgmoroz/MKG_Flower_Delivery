from django import template

register = template.Library()

@register.simple_tag
def status_css(order):
    return {
        'PENDING':    'pending',
        'PROCESSING': 'processing',
        'DELIVERING': 'delivering',
        'COMPLETED':  'completed'
    }.get(order.status, 'pending')
