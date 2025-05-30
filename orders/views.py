from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.contrib import messages
import datetime
from .email_utils import send_order_confirmation
from catalog.models import Product
from .models import Order, OrderItem
from django.urls import reverse
from bot.utils import send_order_status_update

# Рабочие дни: понедельник=0 … пятница=4
WORK_DAYS = set(range(0, 5))
WORK_START = 9   # 09:00
WORK_END = 17  # 18:00 (заказы до 17:59)


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

    # Подготовка данных корзины для шаблона
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

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        # Проверка рабочего времени
        now = timezone.localtime(timezone.now())
        if now.weekday() not in WORK_DAYS or not (WORK_START <= now.hour < WORK_END):
            messages.error(
                request,
                'Заказы принимаются только в рабочее время: Пн–Пт с 09:00 до 18:00.'
            )
            return render(request, 'orders/checkout.html', {
                'form': form,
                'cart_items': cart_items,
                'total_sum': total_sum,
            })

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

            # Уведомление Telegram
            from bot.utils import send_new_order_notification
            base_url = request.build_absolute_uri('/').rstrip('/')
            send_new_order_notification(order, base_url)

            # Очищаем корзину
            request.session['cart'] = {}

            # Отправка e-mail клиенту
            send_order_confirmation(order)

            return redirect('orders:thank_you', order_id=order.id)

    else:
        # GET: предварительно подставляем адрес пользователя
        initial = {}
        if request.user.address:
            initial['delivery_address'] = request.user.address
        form = CheckoutForm(initial=initial)

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
    return redirect('catalog:cart')


@login_required
def thank_you(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'orders/thank_you.html', {'order': order})


# --- список заказов ----------------------------------------------
def manage_orders(request):
    orders = (
        Order.objects
        .select_related("user")
        .order_by("-created_at")
    )
    return render(request, "orders/manage.html", {"orders": orders})


# --- смена статуса по кнопке --------------------------------------
def set_order_status(request, order_id, status):
    order = get_object_or_404(Order, pk=order_id)
    if order.status != status:
        order.status = status
        order.save()
        send_order_status_update(order)  # Telegram/бот
    return redirect(reverse("orders:manage_orders"))