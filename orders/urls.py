from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('history/', views.order_history, name='history'),
    path('repeat/<int:order_id>/', views.repeat_order, name='repeat'),
    path('thankyou/<int:order_id>/', views.thank_you, name='thank_you'),
]