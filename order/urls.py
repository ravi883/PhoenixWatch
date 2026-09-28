from django.urls import path
from .views import *

urlpatterns = [
    path("create-order/",create_order_view, name="create-order"),
    path("order-payment/",order_payment_view, name="order-payment"),
    path("order-history/",order_history_view, name="order-history"),
    path(
        "verify-razorpay-payment/",
        verify_razorpay_payment,
        name="verify_razorpay_payment",
    ),
    path(
        "order-success/<str:order_id>/",
        order_success_view,
        name="order_success",
    ),
]
