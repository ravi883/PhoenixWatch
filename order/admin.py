from django.contrib import admin

from .models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderDeliveryDetail,
    OrderBillingDetail,
    OrderPaymentDetail,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "product",
        "product_name",
        "quantity",
        "unit_price",
        "total_price",
    )
    readonly_fields = (
        "product",
        "product_name",
        "unit_price",
        "total_price",
        "quantity"
    )


class OrderStatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 0
    fields = (
        "status",
        "note",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "note",
        "status"
    )


class OrderDeliveryDetailsInline(admin.StackedInline):
    model = OrderDeliveryDetail
    extra = 0

    fields = (
        "first_name",
        "last_name",
        "phone_number",
        "address",
        "city",
        "state",
        "country",
        "pincode",
    )


class OrderBillingDetailsInline(admin.StackedInline):
    model = OrderBillingDetail
    extra = 0

    fields = (
        "first_name",
        "last_name",
        "phone_number",
        "address",
        "city",
        "state",
        "country",
        "pincode",
    )


class OrderPaymentDetailsInline(admin.StackedInline):
    model = OrderPaymentDetail
    extra = 0

    fields = (
        "total_amount",
        "advance_amount",
        "remaining_amount",
        "status",
        "payment_method",
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_id",
        "customer",
        "status",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order_id",
        "customer__email",
        "customer__phone_number",
    )

    readonly_fields = (
        "customer",
        "order_id",
        # "sub_total",
        # "total_amount",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    inlines = (
        OrderItemInline,
        OrderStatusInline,
        OrderDeliveryDetailsInline,
        OrderPaymentDetailsInline,
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product",
        "product_name",
        "quantity",
        "unit_price",
        "total_price",
        "created_at",
    )

    search_fields = (
        "order__order_id",
        "product_name",
        "product__name",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "status",
        "note",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_id",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(OrderDeliveryDetail)
class OrderDeliveryDetailsAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "first_name",
        "last_name",
        "phone_number",
        "city",
        "state",
        "pincode",
    )

    search_fields = (
        "order__order_id",
        "first_name",
        "last_name",
        "phone_number",
        "city",
        "pincode",
    )


@admin.register(OrderBillingDetail)
class OrderBillingDetailsAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "first_name",
        "last_name",
        "phone_number",
        "city",
        "state",
        "pincode",
    )

    search_fields = (
        "order__order_id",
        "first_name",
        "last_name",
        "phone_number",
        "city",
        "pincode",
    )


@admin.register(OrderPaymentDetail)
class OrderPaymentDetailsAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "total_amount",
        "advance_amount",
        "remaining_amount",
        "status",
        "payment_method",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order__order_id",
        "razorpay_order_id",
        "razorpay_payment_id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )