
from .models import Cart


def cart_context(request):
    customer_id = request.session.get("customer_id")
    cart = None

    if customer_id:
        cart = Cart.objects.filter(
            customer_id=customer_id
        ).first()

    else:
        session_key = request.session.session_key

        if session_key:
            cart = Cart.objects.filter(
                session_key=session_key,
                customer=None,
            ).first()

    if cart:
        cart_items = cart.items.select_related(
            "product"
        ).prefetch_related(
            "product__images"
        )
        cart_count = cart.total_items
    else:
        cart_items = []
        cart_count = 0

    return {
        "cart": cart,
        "cart_items": cart_items,
        "cart_count": cart_count,
    }
