from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from products.models import Products

from .models import CartItem
from .utils import get_or_create_cart


# =========================================================
# CART PAGE
# =========================================================

def cart_view(request):

    cart = get_or_create_cart(request)

    cart_items = (cart.items.select_related("product").prefetch_related("product__images"))
    context = {
        "cart": cart,
        "cart_items": cart_items,
    }

    return render(
        request,
        "customers/templates/cart.html",
        context
    )


# =========================================================
# ADD TO CART
# =========================================================

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Products,
        product_id=product_id,
        is_active=True,
    )
    cart = get_or_create_cart(request)
    # Get quantity
    try:
        quantity = int(request.POST.get("quantity", 1))

    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    # -----------------------------------
    # STOCK CHECK
    # -----------------------------------

    if product.stock <= 0:
        return JsonResponse({"success": False,"message": "This product is out of stock."}, status=400)

    # -----------------------------------
    # GET / CREATE ITEM
    # -----------------------------------

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            "quantity": quantity
        }
    )

    # -----------------------------------
    # ITEM ALREADY EXISTS
    # -----------------------------------

    if not created:

        new_quantity = (
            cart_item.quantity + quantity
        )

        if new_quantity > product.stock:

            return JsonResponse({
                "success": False,
                "message": (
                    f"Only {product.stock} "
                    "items are available."
                ),
            }, status=400)

        cart_item.quantity = new_quantity

        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

    # -----------------------------------
    # RESPONSE
    # -----------------------------------

    return JsonResponse({
        "success": True,
        "message": "Product added to cart.",
        "cart_count": cart.total_items,
        "subtotal": str(cart.subtotal),
    })


# =========================================================
# UPDATE QUANTITY
# =========================================================

@require_POST
def update_cart_item(request, item_id):
    print("item:",item_id)
    cart = get_or_create_cart(request)

    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        quantity = int(request.POST.get("quantity"))
    except (TypeError, ValueError):

        return JsonResponse({
            "success": False,
            "message": "Invalid quantity.",
        }, status=400)

    # -----------------------------------
    # DELETE IF ZERO
    # -----------------------------------

    if quantity < 1:
        return JsonResponse({
            "success": False,
            "message": "Quantity must be at least 1."
        })

    if quantity > cart_item.product.stock:
        return JsonResponse({
            "success": False,
            "message": f"Only {cart_item.product.stock} items are available."
        })

    cart_item.quantity = quantity
    cart_item.save(update_fields=["quantity", "updated_at"])

    # return JsonResponse({
    #     "success": True,
    #     "quantity": cart_item.quantity,
    #     "subtotal": str(cart.subtotal),
    #     "cart_count": cart.total_items,
    # })


    return JsonResponse({
        "success": True,
        "quantity": cart_item.quantity,
        "line_total": str(
            cart_item.line_total
        ),
        "cart_count": cart.total_items,
        "subtotal": str(cart.subtotal),
    })


# =========================================================
# REMOVE ITEM
# =========================================================

@require_POST
def remove_cart_item(request, item_id):

    # Get current user's cart
    cart = get_or_create_cart(request)

    try:
        # Find the cart item
        item = CartItem.objects.get(id=item_id)
    except CartItem.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Cart item does not exist."
        }, status=404)

    # Make sure this item belongs to current cart
    if item.cart_id != cart.id:
        return JsonResponse({
            "success": False,
            "message": "This item does not belong to your cart."
        }, status=403)

    # Delete item
    item.delete()

    # Return updated cart information
    return JsonResponse({
        "success": True,
        "message": "Item removed successfully.",
        "cart_count": cart.total_items,
        "subtotal": str(cart.subtotal),
    })

# =========================================================
# CLEAR CART
# =========================================================

@require_POST
def clear_cart(request):

    cart = get_or_create_cart(request)

    cart.items.all().delete()

    return JsonResponse({
        "success": True,
        "message": "Cart cleared.",
        "cart_count": 0,
        "subtotal": "0.00",
    })


# =========================================================
# CART COUNT
# =========================================================

def cart_count(request):

    cart = get_or_create_cart(request)

    return JsonResponse({
        "cart_count": cart.total_items
    })

def cart_drawer_view(request):
    cart = get_or_create_cart(request)

    cart_items = cart.items.select_related("product").prefetch_related("product__images")
    print("cart:-",cart_items)
    return render(
        request,
        "cart-drawer-items.html",
        {
            "cart": cart,
            "cart_items": cart_items,
        }
    )