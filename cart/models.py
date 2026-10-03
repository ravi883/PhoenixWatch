from django.db import models
from django.core.validators import MinValueValidator

from customers.models import Customer,BaseModel
from products.models import Products
from order.models import Coupon
from decimal import Decimal, ROUND_HALF_UP

class Cart(models.Model):
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,related_name="cart",null=True,blank=True)
    session_key = models.CharField(max_length=100,unique=True,null=True,blank=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "cart"

    def __str__(self):
        if self.customer:
            return f"Cart - {self.customer.email}"

        return f"Guest Cart - {self.session_key}"

    @property
    def total_items(self):
        return sum(
            item.quantity
            for item in self.items.all()
        )

    @property
    def subtotal(self):
        cart_total = sum(
                    item.line_total
                    for item in self.items.select_related("product")
                    )
            
        if self.coupon:
            total_discount = ((cart_total * Decimal(self.coupon.discount_percentage))/100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)            
            return cart_total - total_discount
        return cart_total

    @property
    def discount_price(self):
        cart_total = sum(
            item.line_total
            for item in self.items.select_related("product")
        )

        if not self.coupon:
            return Decimal("0.00")

        return ((cart_total * Decimal(self.coupon.discount_percentage))/100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")

    product = models.ForeignKey( Products,on_delete=models.PROTECT,related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1,
        validators=[
            MinValueValidator(1)
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart_item"

        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_in_cart",
            )
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.product.price * self.quantity