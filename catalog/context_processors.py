from .cart_utils import get_cart, total_items

def cart_stats(request):
    cart = get_cart(request)
    return {
        'cart_items_total': total_items(cart)
    }
