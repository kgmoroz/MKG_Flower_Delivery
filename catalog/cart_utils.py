def get_cart(request):
    """Берём корзину из сессии (или пустой словарь)."""
    return request.session.get('cart', {})


def save_cart(request, cart: dict):
    """Кладём корзину в сессию и помечаем её изменённой."""
    request.session['cart'] = cart
    request.session.modified = True


def total_items(cart: dict) -> int:
    """Сколько всего штук (а не позиций) в корзине."""
    return sum(cart.values())
