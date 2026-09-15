from django.db import models
from django.core.validators import MinValueValidator

from customers.models import Customer,BaseModel
from products.models import Products


class Cart(models.Model):
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,related_name="cart",null=True,blank=True)
    session_key = models.CharField(max_length=100,unique=True,null=True,blank=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return sum(
            item.line_total
            for item in self.items.select_related("product")
        )


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