from .utils import get_or_create_cart


def cart_context(request):
    cart = get_or_create_cart(request)

    return {
        "cart": cart,
        "cart_items": cart.items.select_related("product").prefetch_related("product__images"),
        "cart_count": cart.total_items,
    }