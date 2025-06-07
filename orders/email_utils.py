from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_order_confirmation(order):
    # Заполняем контекст для шаблона письма
    context = {
        'order': order,
        'items': order.items.all(),
        'total': sum(i.quantity * i.price for i in order.items.all())
    }
    subject = f"Ваш заказ №{order.id} принят"
    # HTML-тело
    html_body = render_to_string('emails/order_confirmation.html', context)
    # Плэйн-текст (можно тот же контекст, если понадобится)
    text_body = render_to_string('emails/order_confirmation.txt', context)

    send_mail(
        subject=subject,
        message=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=html_body,
    )
