from django.conf import settings
from django.core.mail import EmailMultiAlternatives


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