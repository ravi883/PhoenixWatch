from django.contrib import messages
from django.shortcuts import redirect, render
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
    return render(request,"track_orders.html")

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

    OrderPaymentDetail.objects.create(
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

    return redirect(
        "order-payment",
    )

def order_payment_view(request):
    return render(request, "order_payment.html")