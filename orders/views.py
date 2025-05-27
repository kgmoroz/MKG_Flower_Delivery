from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone

from catalog.models import Product
from .models import Order, OrderItem

# Форма оформления заказа
class CheckoutForm(forms.Form):
    delivery_date = forms.DateField(label='Дата доставки', widget=forms.DateInput(attrs={'type': 'date'}))
    delivery_time = forms.TimeField(label='Время доставки', widget=forms.TimeInput(attrs={'type': 'time'}))
    delivery_address = forms.CharField(label='Адрес доставки', max_length=255)

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('catalog:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Создаём заказ
            order = Order.objects.create(
                user=request.user,
                status='PENDING',
                delivery_date=form.cleaned_data['delivery_date'],
                delivery_time=form.cleaned_data['delivery_time'],
                delivery_address=form.cleaned_data['delivery_address']
            )
            # Создаём позиции заказа
            for pid, qty in cart.items():
                product = get_object_or_404(Product, pk=pid)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=product.price
                )
            # Очищаем корзину
            request.session['cart'] = {}
            return redirect('orders:history')
    else:
        form = CheckoutForm()

    # Для отображения корзины на странице оформления
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [
        {
            'product': p,
            'quantity': cart[str(p.id)],
            'total': p.price * cart[str(p.id)]
        }
        for p in products
    ]
    total_sum = sum(item['total'] for item in cart_items)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_sum': total_sum,
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})

@login_required
def repeat_order(request, order_id):
    original = get_object_or_404(Order, pk=order_id, user=request.user)
    # Восстанавливаем корзину из старого заказа
    new_cart = {str(item.product.id): item.quantity for item in original.items.all()}
    request.session['cart'] = new_cart
    return redirect('orders:checkout')