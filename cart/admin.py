from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):

    model = CartItem

    extra = 0

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "session_key",
        "total_items",
        "subtotal",
        "updated_at",
    )

    search_fields = (
        "customer__email",
        "customer__phone_number",
        "session_key",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [
        CartItemInline
    ]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "line_total",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__product_id",
    )

    list_select_related = (
        "cart",
        "product",
    )