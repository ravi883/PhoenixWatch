import logging

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings


logger = logging.getLogger(__name__)


def send_whatsapp_message(phone_number, order):
    """
    Sends WhatsApp message through Twilio.

    IMPORTANT:
    Any Twilio failure is caught here.
    It will NOT break the Razorpay/order flow.
    """

    message = (
    f"Hi {order.delivery_details.first_name},\n\n"
    f"Your PhoenixWatch order {order.order_id} has been confirmed successfully.\n\n"
    f"Order Amount: ₹{order.total_amount}\n"
    f"Payment Status: {order.payment_details.status}\n\n"
    "Thank you for shopping with PhoenixWatch!"
)
    
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
        )
        
        # Make sure number is in E.164 format
        if not phone_number:
            logger.warning("WhatsApp message skipped: phone number is empty.")
            return {
                "success": False,
                "error": "Phone number is empty.",
            }

        if not phone_number.startswith("+"):
            phone_number = f"+91{phone_number}"

        twilio_message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{phone_number}",
            body=message,
        )

        logger.info(
            "WhatsApp message sent successfully. SID=%s",
            twilio_message.sid,
        )
        print("Success")
        return {
            "success": True,
            "sid": twilio_message.sid,
        }

    except TwilioRestException as e:

        logger.error(
            "Twilio WhatsApp error. "
            "Code=%s Status=%s Message=%s",
            e.code,
            e.status,
            e.msg,
            exc_info=True,
        )

        return {
            "success": False,
            "error": str(e),
            "code": e.code,
            "status": e.status,
        }

    except Exception as e:

        logger.error(
            "Unexpected WhatsApp error: %s",
            str(e),
            exc_info=True,
        )

        return {
            "success": False,
            "error": str(e),
        }
    