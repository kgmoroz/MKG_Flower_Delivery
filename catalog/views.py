from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, render, get_object_or_404
from .models import Product
from .cart_utils import get_cart, save_cart
from django.db.models import F


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12    # 12 товаров на страницу

    def get_ordering(self):
        """Смотрим ?sort=price_asc / price_desc / name"""
        sort = self.request.GET.get('sort', 'name')
        mapping = {
            'price_asc':  'price',
            'price_desc': '-price',
            'name':       'name',
        }
        return mapping.get(sort, 'name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_sort'] = self.request.GET.get('sort', 'name')
        return ctx


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
