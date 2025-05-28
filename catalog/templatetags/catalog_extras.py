from urllib.parse import urlencode
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_with_sort(context, sort_value):
    """Сохраняем текущую страницу (?page=N) и меняем/ставим sort=""."""
    request = context['request']
    params = request.GET.copy()
    params['sort'] = sort_value
    return f"{request.path}?{urlencode(params)}"
