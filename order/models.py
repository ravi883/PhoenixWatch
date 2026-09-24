import uuid
from decimal import Decimal

from django.db import models


# Create your models here.
def generate_order_id():
    return f"ORD{uuid.uuid4().hex[:10].upper()}"


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=50)
    discount_percentage = models.IntegerField(default=10)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_code

class Order(BaseModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        RETURNED = "returned", "Returned"

    order_id = models.CharField(max_length=20, unique=True, editable=False, default=generate_order_id)
    customer = models.ForeignKey("customers.Customer",on_delete=models.PROTECT,related_name="orders")
    status = models.CharField(max_length=30,choices=Status.choices,default=Status.PENDING,db_index=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_id

class OrderItem(BaseModel):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items" )
    product = models.ForeignKey("products.Products", on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_item"

    def __str__(self):
        return f"{self.order.order_id} - {self.product_name}"

class OrderStatus(BaseModel):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=30, choices=Order.Status.choices)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "order_status"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.order.order_id} - {self.status}"

class OrderPaymentDetail(BaseModel):

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ADVANCE_PENDING = "advance_pending", "Advance Pending"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        PRE_PAID = "pre_paid", "Pre Paid"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class PaymentMethod(models.TextChoices):
        RAZORPAY = "razorpay", "Razorpay"
        COD = "cod", "Cash on Delivery"
 
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment_details")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30,  choices=PaymentStatus.choices, default=PaymentStatus.ADVANCE_PENDING, db_index=True)
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.RAZORPAY,)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "order_payment_detail"

    def __str__(self):
        return f"Payment - {self.order.order_id}"

class OrderDeliveryDetail(BaseModel):
    order = models.OneToOneField(Order,on_delete=models.CASCADE, related_name="delivery_details",)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)

    class Meta:
        db_table = "order_delivery_detail"

    def __str__(self):
        return f"Delivery - {self.order.order_id}"


class OrderBillingDetail(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="billing_details")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)

    class Meta:
        db_table = "order_billing_detail"

    def __str__(self):
        return f"Billing - {self.order.order_id}"