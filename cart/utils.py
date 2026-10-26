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

def merge_guest_cart_to_customer(request, customer):
    """
    Merge guest cart items into the logged-in customer's cart.
    """

    session_key = request.session.session_key

    if not session_key:
        return

    guest_cart = Cart.objects.filter(
        session_key=session_key,
        customer=None,
    ).first()

    if not guest_cart:
        return

    guest_cart.session_key = None
    guest_cart.customer = customer

    guest_cart.save()

