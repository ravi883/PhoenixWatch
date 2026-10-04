from .models import Cart
from customers.models import Customer

def get_or_create_cart(request):
    """
    Get the current customer's cart.

    Logged-in customer:
        Customer cart

    Guest:
        Session-based cart
    """

    customer_id = request.session.get("customer_id")

    # -----------------------------------
    # LOGGED-IN CUSTOMER
    # -----------------------------------

    if customer_id:
        customer = Customer.objects.get(id=customer_id)

        cart, created = Cart.objects.get_or_create(
            customer_id=customer_id
        )

        return cart

    # -----------------------------------
    # GUEST CUSTOMER
    # -----------------------------------

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        session_key=session_key,
        customer=None,
    )

    return cart