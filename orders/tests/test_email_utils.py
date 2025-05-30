import pytest
from django.conf import settings
from orders.email_utils import send_order_confirmation

@pytest.mark.django_db
def test_send_order_confirmation(monkeypatch, order):
    sent = {
        'render_calls': []
    }

    # 1) Подменяем render_to_string, чтобы отследить, какие шаблоны и контекст используются
    def fake_render_to_string(template_name, context):
        sent['render_calls'].append((template_name, context))
        return f"RENDERED({template_name})"

    monkeypatch.setattr(
        'orders.email_utils.render_to_string',
        fake_render_to_string
    )

    # 2) Подменяем send_mail, чтобы перехватить его аргументы
    def fake_send_mail(subject, message, from_email, recipient_list, html_message):
        sent['subject']        = subject
        sent['message']        = message
        sent['from_email']     = from_email
        sent['recipient_list'] = recipient_list
        sent['html_message']   = html_message

    monkeypatch.setattr(
        'orders.email_utils.send_mail',
        fake_send_mail
    )

    # 3) Вызываем вашу функцию
    send_order_confirmation(order)

    # 4) Проверяем вызов send_mail
    assert sent['subject'] == f"Ваш заказ №{order.id} принят"
    assert sent['from_email'] == settings.DEFAULT_FROM_EMAIL
    assert sent['recipient_list'] == [order.user.email]
    assert sent['message']      == "RENDERED(emails/order_confirmation.txt)"
    assert sent['html_message'] == "RENDERED(emails/order_confirmation.html)"

    # 5) Проверяем, что шаблоны рендерятся с правильным контекстом
    # Должно быть два вызова: HTML и текстовый
    templates = [tpl for tpl, _ in sent['render_calls']]
    assert "emails/order_confirmation.html" in templates
    assert "emails/order_confirmation.txt"  in templates

    # И контекст должен содержать ключи 'order', 'items' и 'total'
    for tpl, ctx in sent['render_calls']:
        assert 'order' in ctx
        assert 'items' in ctx
        assert 'total' in ctx
        # проверяем, что total действительно равен сумме позиций
        expected = sum(i.quantity * i.price for i in order.items.all())
        assert ctx['total'] == expected
