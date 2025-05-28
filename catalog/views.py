from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, render, get_object_or_404
from .models import Product
from .cart_utils import get_cart, save_cart


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [
        {'product': p, 'quantity': cart[str(p.id)], 'total': p.price * cart[str(p.id)]}
        for p in products
    ]
    total_sum = sum(item['total'] for item in cart_items)
    return render(request, 'catalog/cart.html', {'cart_items': cart_items, 'total_sum': total_sum})


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('catalog:cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('catalog:cart')


def update_cart(request, product_id, action):
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)

    pid = str(product.id)
    qty = cart.get(pid, 0)

    if action == 'inc':
        cart[pid] = qty + 1
    elif action == 'dec':
        if qty > 1:
            cart[pid] = qty - 1
        else:          # если было 1, удаляем позицию
            cart.pop(pid, None)
    elif action == 'remove':
        cart.pop(pid, None)

    save_cart(request, cart)
    return redirect('catalog:cart')
