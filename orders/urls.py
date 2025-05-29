from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('history/', views.order_history, name='history'),
    path('repeat/<int:order_id>/', views.repeat_order, name='repeat'),
    path('thankyou/<int:order_id>/', views.thank_you, name='thank_you'),
    path(
        "manage/",
        staff_member_required(views.manage_orders),
        name="manage_orders",
    ),
    path(
        "manage/<int:order_id>/set/<str:status>/",
        staff_member_required(views.set_order_status),
        name="set_order_status",
    ),
]