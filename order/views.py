from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from cart.models import *
from decimal import Decimal, ROUND_HALF_UP
from order.models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderDeliveryDetail,
    OrderBillingDetail,
    OrderPaymentDetail,

)
from django.db import transaction
from .forms import TrackOrderForm
from django.http import HttpResponseRedirect
from .razorpay_client import razorpay_client
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
import razorpay
import json
import logging
from .utils import send_order_confirmation_email
from .whatsapp import send_whatsapp_message


logger = logging.getLogger(__name__)    

def track_order_view(request):
    order = None

    if request.method == "POST":
        form = TrackOrderForm(request.POST)

        if form.is_valid():

            order_id = form.cleaned_data["order_id"].strip()
            if not order_id:
                messages.error(request, "Enter Order ID.",extra_tags="coupon")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            email = form.cleaned_data["email"].strip().lower()
            
            if not email:
                messages.error(request, "Enter Email ID.",extra_tags="coupon")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            try:
                order = Order.objects.select_related("customer").get(
                    order_id=order_id,
                    customer__email__iexact=email,
                )

            except Order.DoesNotExist:
                messages.error(request, "No order found with this Order ID and email address.",extra_tags="coupon")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        form = TrackOrderForm()

    return render(
        request,
        "track_orders.html",
        {
            "order": order,
        },
    )


def order_history_view(request):
    customer_id = request.session.get("customer_id")

    if not customer_id:
        return redirect("login")

    all_orders = (
        Order.objects
        .filter(customer_id=customer_id)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status", "all")

    if status_filter == "transit":
        orders = all_orders.filter(
            status__in=[
                Order.Status.CONFIRMED,
                Order.Status.PROCESSING,
                Order.Status.SHIPPED,
                Order.Status.OUT_FOR_DELIVERY,
            ]
        )

    elif status_filter == "delivered":
        orders = all_orders.filter(status=Order.Status.DELIVERED)

    else:
        orders = all_orders

    delivered_orders = all_orders.filter(status=Order.Status.DELIVERED)

    transit_orders = all_orders.filter(
        status__in=[
            Order.Status.CONFIRMED,
            Order.Status.PROCESSING,
            Order.Status.SHIPPED,
            Order.Status.OUT_FOR_DELIVERY,
        ]
    )

    context = {
        "orders": orders,
        "all_orders": all_orders,
        "delivered_orders": delivered_orders,
        "transit_orders": transit_orders,
        "status_filter": status_filter,
    }

    return render(request, "order_history.html",context)
    

@transaction.atomic
def create_order_view(request):

    if request.method != "POST":
        return redirect("checkout")

    # Get customer
    customer_id = request.session.get("customer_id")
    
    if not customer_id:
        messages.warning(request,"Please login before proceeding.")
        return redirect("login")

    try:
        customer = Customer.objects.get( id=customer_id)
    except Customer.DoesNotExist:
        request.session.pop("customer_id", None)
        messages.error( request, "Customer account not found.")
        return redirect("login")

    # PAYMENT TYPE
    payment_type = request.POST.get("payment_type", "").strip()
    
    if payment_type not in ["prepaid", "pay_now"]:
        return JsonResponse({
            "success": False,
            "message": "Invalid payment option."
        }, status=400)

    # Get cart
    cart = Cart.objects.filter(customer=customer).first()

    if not cart:
        messages.warning(request,"Your cart is empty.")
        return redirect("cart")

    # Get cart items
    cart_items = list( CartItem.objects.filter(cart=cart).select_related("product"))

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    locked_products = {}

    for item in cart_items:
        product = (Products.objects.select_for_update().get(pk=item.product.pk))
        locked_products[product.pk] = product

        if product.stock < item.quantity:
            messages.error( request, f"Only {product.stock} unit(s) of "f"{product.name} are available." )
            return redirect("checkout")

    subtotal = cart.subtotal
    # ----------------------------------------------------------
    # 20% ADVANCE
    # ----------------------------------------------------------

    advance_percentage = Decimal("20.00")
    advance_amount = ( subtotal * advance_percentage / Decimal("100")).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    remaining_amount = (subtotal - advance_amount).quantize( Decimal("0.01"),rounding=ROUND_HALF_UP)

    if payment_type == "prepaid":
        amount_to_pay = subtotal

    else:
        amount_to_pay = advance_amount

    amount_to_pay = amount_to_pay.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
    # ----------------------------------------------------------
    # DELIVERY DETAILS
    # ----------------------------------------------------------
    shipping_first_name = request.POST.get("shipping_first_name", "").strip()
    shipping_last_name = request.POST.get("shipping_last_name","").strip()
    shipping_phone = request.POST.get("shipping_phone", "").strip()
    shipping_address  = request.POST.get("shipping_address","").strip()
    shipping_city = request.POST.get("shipping_city", "").strip()
    shipping_state = request.POST.get("shipping_state", "").strip()
    shipping_country  = request.POST.get("shipping_country", "").strip()
    shipping_pincode = request.POST.get( "shipping_pincode","").strip()

    shipping_fields = [shipping_first_name, shipping_last_name, shipping_phone,shipping_address, shipping_city, shipping_state, shipping_country, shipping_pincode,]

    if not all(shipping_fields):

        messages.error(request,"Please complete all shipping address fields.")
        return redirect("checkout")

    billing_option = request.POST.get("billing_option","same")

    if billing_option == "same":

        billing_first_name = shipping_first_name
        billing_last_name = shipping_last_name
        billing_phone = shipping_phone
        billing_address = shipping_address
        billing_city = shipping_city
        billing_state = shipping_state
        billing_country = shipping_country
        billing_pincode = shipping_pincode
        billing_email = customer.email

    elif billing_option == "different":

        billing_first_name = request.POST.get("billing_first_name","" ).strip()
        billing_last_name = request.POST.get("billing_last_name", "").strip()
        billing_phone = request.POST.get("billing_phone_number","").strip()
        billing_address = request.POST.get("billing_address","").strip()
        billing_city = request.POST.get("billing_city","").strip()
        billing_state = request.POST.get("billing_state","").strip()
        billing_country = request.POST.get("billing_country","").strip()
        billing_pincode = request.POST.get("billing_pincode","").strip()
        billing_email = request.POST.get("billing_email","").strip()

    # ----------------------------------------------------------
    # BASIC SERVER VALIDATION
    # ----------------------------------------------------------

        billing_fields = [billing_first_name, billing_last_name, billing_phone, billing_address,  billing_city,  billing_state,  billing_country, billing_pincode, billing_email ]

        if not all(billing_fields):
            messages.error(request, "Please complete all billing address fields." )
            return redirect("checkout")
    else:
        messages.error(request,"Invalid billing option.")
        return redirect("checkout")

    if not customer.address:
        customer.address = shipping_address

    if not customer.city:
        customer.city = shipping_city

    if not customer.state:
        customer.state = shipping_state

    if not customer.country:
        customer.country = shipping_country

    if not customer.pincode:
        customer.pincode = shipping_pincode

    customer.save()
    # ----------------------------------------------------------
    # CREATE ORDER
    # ----------------------------------------------------------

    order = Order.objects.create(
        customer=customer,
        status=Order.Status.PENDING,
        subtotal=subtotal,
        total_amount=subtotal,
        coupon = cart.coupon,
        coupon_code = cart.coupon_code,
        discount_amount = cart.discount_amount
    )

    # ----------------------------------------------------------
    # CREATE ORDER ITEMS
    # ----------------------------------------------------------

    order_items = []

    for item in cart_items:

        unit_price = ( item.product.price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_price = ( unit_price * item.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        order_items.append(
            OrderItem(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
        )

    OrderItem.objects.bulk_create(
        order_items
    )

    # ----------------------------------------------------------
    # ORDER STATUS
    # ----------------------------------------------------------

    OrderStatus.objects.create(
        order=order,
        status=Order.Status.PENDING,
        note="Order created.",
    )

    # ----------------------------------------------------------
    # DELIVERY
    # ----------------------------------------------------------

    OrderDeliveryDetail.objects.create(
        order=order,
        first_name=shipping_first_name,
        last_name=shipping_last_name,
        phone_number=shipping_phone,
        address=shipping_address,
        city=shipping_city,
        state=shipping_state,
        country=shipping_country,
        pincode=shipping_pincode,
    )

    # ----------------------------------------------------------
    # BILLING
    # ----------------------------------------------------------

    OrderBillingDetail.objects.create(
        order=order,
        first_name=billing_first_name,
        last_name=billing_last_name,
        phone_number=billing_phone,
        address=billing_address,
        city=billing_city,
        state=billing_state,
        country=billing_country,
        pincode=billing_pincode,
        email = billing_email
    )

    # ----------------------------------------------------------
    # PAYMENT DETAILS
    # ----------------------------------------------------------

    payment_detail = OrderPaymentDetail.objects.create(
        order=order,
        total_amount=subtotal,
        advance_amount=advance_amount,
        remaining_amount=remaining_amount,
        status=(
            OrderPaymentDetail
            .PaymentStatus
            .ADVANCE_PENDING
        ),
        payment_method=(
            OrderPaymentDetail
            .PaymentMethod
            .RAZORPAY
        ),
    )

    # Don't clear cart yet.
    # Clear it after successful Razorpay payment.

    amount_in_paise = int(
        amount_to_pay * Decimal("100")
    )

    razorpay_order = razorpay_client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": order.order_id,
        "notes": {
            "order_id": order.order_id,
            "customer_id": str(customer_id),
            "payment_type": payment_type,
        },
    })

    payment_detail.razorpay_order_id = (
        razorpay_order["id"]
    )

    payment_detail.save(
        update_fields=["razorpay_order_id"]
    )

    response = {
        "success": True,
        "order_id": order.order_id,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": amount_in_paise,
        "amount_display": str(amount_to_pay),
        "payment_type": payment_type,
        "customer": {
            "name": (
                f"{customer.first_name} "
                f"{customer.last_name}"
            ).strip(),

            "email": customer.email,
            "contact": customer.phone_number,
        },
    }
    return JsonResponse(response)


def order_payment_view(request):
    customer_id = request.session.get("customer_id")

    if not customer_id:
        messages.warning(request, "Please login before proceeding.")
        return redirect("login")

    order = (
    Order.objects
    .select_related("payment_details", "customer")
    .filter(
        customer_id=customer_id,
        status=Order.Status.PENDING,
    )
    .order_by("-created_at")
    .first()
)

    payment_detail = order.payment_details

    # Already paid
    if payment_detail.status in [
        OrderPaymentDetail.PaymentStatus.PARTIALLY_PAID,
        OrderPaymentDetail.PaymentStatus.PRE_PAID,
        OrderPaymentDetail.PaymentStatus.PAID,
    ]:
        return redirect("order-success", order_id=order.order_id)

    if not payment_detail.razorpay_order_id:

        amount_in_paise = int(
            payment_detail.advance_amount * 100
        )

        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": order.order_id,
            "notes": {
                "order_id": order.order_id,
                "customer_id": str(customer_id),
            },
        })

        payment_detail.razorpay_order_id = razorpay_order["id"]
        payment_detail.save(
            update_fields=["razorpay_order_id"]
        )

        context = {
            "order": order,
            "payment_detail": payment_detail,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        }

    return render(request, "order_payment.html", context)


@require_POST
@transaction.atomic
def verify_razorpay_payment(request):

    customer_id = request.session.get("customer_id")

    if not customer_id:

        return JsonResponse({
            "success": False,
            "message": "Please login again."
        }, status=401)

    
    data = json.loads(request.body)
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")
    order_id = data.get("order_id")


    if not all([
        razorpay_payment_id,
        razorpay_order_id,
        razorpay_signature,
        order_id,
    ]):

        return JsonResponse({
            "success": False,
            "message": "Invalid payment response."
        }, status=400)

    # ==========================================================
    # GET ORDER
    # ==========================================================

    try:

        order = (
            Order.objects
            .select_for_update()
            .select_related(
                "customer",
            )
            .get(
                order_id=order_id,
                customer_id=customer_id,
            )
        )

    except Order.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "Order not found."
        }, status=404)

    payment_detail = order.payment_details

    # ==========================================================
    # VERIFY RAZORPAY ORDER ID
    # ==========================================================

    if (
        payment_detail.razorpay_order_id
        != razorpay_order_id
    ):

        return JsonResponse({
            "success": False,
            "message": "Invalid Razorpay order."
        }, status=400)

    # ==========================================================
    # VERIFY SIGNATURE
    # ==========================================================

    try:

        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

    except razorpay.errors.SignatureVerificationError:

        return JsonResponse({
            "success": False,
            "message": "Payment verification failed."
        }, status=400)

    # ==========================================================
    # CHECK IF ALREADY PAID
    # ==========================================================

    if payment_detail.status in [
        OrderPaymentDetail.PaymentStatus.PARTIALLY_PAID,
        OrderPaymentDetail.PaymentStatus.PRE_PAID,
        OrderPaymentDetail.PaymentStatus.PAID,
    ]:

        return JsonResponse({
            "success": True,
            "message": "Payment already verified.",
            "redirect_url": (
                f"/order-success/{order.order_id}/"
            ),
        })

    # ==========================================================
    # GET RAZORPAY PAYMENT
    # ==========================================================

    razorpay_payment = razorpay_client.payment.fetch(
        razorpay_payment_id
    )

    payment_status = razorpay_payment.get("status")

    if payment_status != "captured":

        return JsonResponse({
            "success": False,
            "message": (
                f"Payment is not captured. "
                f"Current status: {payment_status}"
            )
        }, status=400)

    # ==========================================================
    # AMOUNT VERIFICATION
    # ==========================================================

    paid_amount = Decimal(
        str(razorpay_payment["amount"])
    ) / Decimal("100")

    paid_amount = paid_amount.quantize(
        Decimal("0.01")
    )

    # Determine expected amount.
    #
    # If payment_detail.razorpay_order_id belongs to this order,
    # fetch Razorpay order and verify amount from Razorpay itself.

    razorpay_order = razorpay_client.order.fetch(
        razorpay_order_id
    )

    expected_amount = (
        Decimal(str(razorpay_order["amount"]))
        / Decimal("100")
    )

    expected_amount = expected_amount.quantize(
        Decimal("0.01")
    )

    if paid_amount != expected_amount:

        return JsonResponse({
            "success": False,
            "message": "Payment amount mismatch."
        }, status=400)

    # ==========================================================
    # UPDATE PAYMENT
    # ==========================================================

    payment_detail.razorpay_payment_id = (
        razorpay_payment_id
    )

    payment_detail.razorpay_signature = (
        razorpay_signature
    )

    # ==========================================================
    # DETERMINE PREPAID / 20% PAYMENT
    # ==========================================================

    if paid_amount == payment_detail.total_amount:

        # 100% prepaid
        payment_detail.status = (
            OrderPaymentDetail
            .PaymentStatus
            .PRE_PAID
        )

        payment_detail.advance_amount = Decimal("0.00")
        payment_detail.remaining_amount = Decimal("0.00")

        order.status = Order.Status.CONFIRMED

        status_note = (
            "Full prepaid payment received "
            "successfully."
        )

    else:

        # 20% advance
        payment_detail.status = (
            OrderPaymentDetail
            .PaymentStatus
            .PARTIALLY_PAID
        )

        payment_detail.remaining_amount = (
            payment_detail.total_amount
            - paid_amount
        ).quantize(
            Decimal("0.01")
        )

        order.status = Order.Status.CONFIRMED

        status_note = (
            "20% advance payment received "
            "successfully."
        )
    order.save()
    payment_detail.save()

    # ==========================================================
    # ORDER STATUS
    # ==========================================================

    OrderStatus.objects.create(
        order=order,
        status=Order.Status.CONFIRMED,
        note=status_note,
    )

    # ==========================================================
    # REDUCE STOCK
    # ==========================================================

    order_items = (
        OrderItem.objects
        .filter(order=order)
        .select_related("product")
    )

    for order_item in order_items:

        product = (
            Products.objects
            .select_for_update()
            .get(pk=order_item.product_id)
        )

        if product.stock < order_item.quantity:

            return JsonResponse({
                "success": False,
                "message": (
                    f"Stock is no longer available "
                    f"for {product.name}."
                )
            }, status=400)

        product.stock -= order_item.quantity

        product.save(
            update_fields=["stock"]
        )

    # ==========================================================
    # CLEAR CART
    # ==========================================================

    cart = Cart.objects.filter(
        customer_id=customer_id
    ).first()

    if cart:

        CartItem.objects.filter(
            cart=cart
        ).delete()

        # If your Cart model has these fields:
        cart.coupon = None
        cart.coupon_code = ""
        cart.discount_amount = Decimal("0.00")
        cart.save()

    # ==========================================================
    # SUCCESS
    # ==========================================================

    if not order.confirmation_email_sent:

        send_order_confirmation_email(order)

        order.confirmation_email_sent = True
        order.save(update_fields=["confirmation_email_sent"])

    try:
        whatsapp_result = send_whatsapp_message(
            order.delivery_details.phone_number,
            order,
        )

        if not whatsapp_result.get("success"):
            logger.warning(
                "WhatsApp notification failed for order %s. "
                "Payment/order will remain successful. Error: %s",
                order.order_id,
                whatsapp_result.get("error"),
            )

    except Exception as e:
        # Absolute safety net.
        # Even if whatsapp.py itself has an unexpected error,
        # payment/order processing will continue.

        logger.exception(
            "Unexpected WhatsApp error for order %s. "
            "Payment/order will remain successful.",
            order.order_id,
    )


    return JsonResponse({
        "success": True,
        "message": "Payment successful.",
        "order_id": order.order_id,
        "redirect_url": reverse(
            "order_success",
            kwargs={
                "order_id": order.order_id
            }
        ),
    })

def order_success_view(request, order_id):

    customer_id = request.session.get("customer_id")

    if not customer_id:
        return redirect("login")

    order = get_object_or_404(Order, order_id=order_id, customer_id=customer_id)

    return render(request, "order-success.html",{"order": order},)
