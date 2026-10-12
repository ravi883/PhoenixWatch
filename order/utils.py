from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import logging
import requests


logger = logging.getLogger(__name__)

def send_order_confirmation_email(order):

    customer = order.customer

    subject = f"Order Confirmed - {order.order_id}"

    text_content = f"""
Hello {customer.first_name},

Thank you for your order!

Your order {order.order_id} has been confirmed.

Order Total: ₹{order.total_amount}

Thank you for shopping with Phoenixwala.

Regards,
PhoenixWatch
"""

    html_content = f"""
    <html>
    <body>
        <h2>Order Confirmed 🎉</h2>

        <p>Hello {customer.first_name},</p>

        <p>
            Thank you for your order!
            Your payment was successful and your order has been confirmed.
        </p>

        <h3>Order Details</h3>

        <p>
            <strong>Order ID:</strong> {order.order_id}
        </p>

        <p>
            <strong>Total Amount:</strong> ₹{order.total_amount}
        </p>

        <p>
            We will update you when your order is shipped.
        </p>

        <p>
            Thank you for shopping with <strong>Phoenixwala</strong>.
        </p>

        <br>

        <p>Regards,<br>
        Phoenixwala Team</p>
    </body>
    </html>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer.email],
    )

    email.attach_alternative(html_content, "text/html")

    email.send(fail_silently=False)


def format_phone_number(phone):
    phone = str(phone).strip()

    if phone.startswith("+91"):
        phone = phone[3:]
    elif phone.startswith("91") and len(phone) == 12:
        phone = phone[2:]

    return phone.strip()

def build_shipment_payload(order):

    if order.payment_details.status == "partially_paid" or order.payment_details.status == "advance_pending":
        pay_mode = "1"
        cod_amount = order.payment_details.remaining_amount
    else:
        pay_mode = "2"
        cod_amount = 0

    order_items = order.items.all()

    product_details = []

    order_amount = 0
    for item in order_items:
        product = item.product
        order_amount += product.price * item.quantity

        product_details.append({
            "product_name": product.name,
            "product_category": str(product.category),
            "product_sku_code": product.product_id,
            "product_tax_rate": "0",
            "product_amount": str(product.price),
            "product_discount": "0",
            "product_quantity": str(item.quantity),
            "product_hsn_code": "hsn",
        })

    payload = {
        "customer_details": {
            "customer_full_name": order.delivery_details.first_name + " " +order.delivery_details.last_name,
            "customer_phone_number": format_phone_number(order.delivery_details.phone_number),
            "customer_full_address": order.delivery_details.address,
            "customer_pincode": order.delivery_details.pincode,
            "customer_order_id": order.order_id,
            "customer_order_date": order.created_at.strftime("%d %B %Y"),
            "customer_address_type": "1",
            "customer_email_id": order.billing_details.email,
            "customer_alternate_phone_number": "",
            "customer_landmark": ""
        },

        "shipment_details": {
            "shipment_package_type": "2",
            "shipment_dead_weight_in_grams": "500",
            "shipment_length": "20",
            "shipment_width": "15",
            "shipment_height": "10",
            "shipment_pickup_warehouse_id": settings.WAREHOUSE_ID,
            "shipment_shipping_mode": "1",
            "shipment_pay_mode": pay_mode,
            "order_amount": str(order_amount),
            "cod_amount": str(cod_amount),
            "commodity_amount": str(order.total_amount),
            "shipping_amount": "0",
            "discount_amount": str(order.discount_amount),
            "discount_coupon_name": order.coupon_code
        },

        "product_details": product_details,

        "shipper_details": {
            "client_code": settings.CLIENT_CODE,
            "user_id": settings.USER_ID,
            "user_secret": settings.DELIVERY_SECRET_KEY
        }
    }
    
    

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            settings.DELIVERY_API_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"message": response.text}

        if response.ok:
            logger.info(
                "QuikShipX API responded successfully. HTTP status: %s",
                response.status_code,
            )
        else:
            logger.error(
                "QuikShipX API returned HTTP %s: %s",
                response.status_code,
                response_data,
            )

        return {
            "success": response.ok,
            "status_code": response.status_code,
            "data": response_data,
        }

    except requests.RequestException:
        logger.exception("QuikShipX API request failed")

        return {
            "success": False,
            "status_code": None,
            "data": {
                "message": "Could not connect to QuikShipX."
            },
        }