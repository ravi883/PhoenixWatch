from django.contrib import admin

from .models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderDeliveryDetail,
    OrderBillingDetail,
    OrderPaymentDetail,
    Coupon
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
        "total_amount",
        "advance_amount",
        "remaining_amount",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_id",
        "customer",
        "status",
        "total_amount",
        "discount_amount",
        "advance_amount_display",
        "remaining_amount_display",
        "payment_status_display",
        "created_at",
    )

    fields = (
        "order_id",
        "customer",
        "coupon",
        "coupon_code",
        "discount_amount",
        "total_amount",
        "status",
        "created_at",
        "updated_at",
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
        "total_amount",
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

    @admin.display(description="Advance Amount")
    def advance_amount_display(self, obj):
        if hasattr(obj, "payment_details"):
            return obj.payment_details.advance_amount
        return "-"

    @admin.display(description="Remaining Amount")
    def remaining_amount_display(self, obj):
        if hasattr(obj, "payment_details"):
            return obj.payment_details.remaining_amount
        return "-"

    @admin.display(description="Payment Status")
    def payment_status_display(self, obj):
        if hasattr(obj, "payment_details"):
            return obj.payment_details.status
        return "-"


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

    readonly_fields=(
        "order_id",
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

    readonly_fields=(
        "order_id",
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

    fields= (
        "order_id",
        "created_at",
        "updated_at",
        "total_amount",
        "advance_amount",
        "remaining_amount",
        "status",
        "payment_method",
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
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
        "order_id",
        "created_at",
        "updated_at",
        "total_amount",
        "advance_amount",
        "remaining_amount",
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
    )

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    # fields = ['id','coupon_code','is_expired']

    list_display=['id','coupon_code','is_expired']