import random
from django.db import models
from customers.models import BaseModel

def generate_code(prefix, digits=6):
    return f"{prefix}{random.randint(10 ** (digits - 1), 10 ** digits - 1)}"

class Categories(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "category"
        
    def __str__(self):
        return self.name


class WatchType(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="watch-type/", null=True, blank=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class StrapType(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="strap-type/", null=True, blank=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Products(BaseModel):
    product_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name="products")
    watch_type = models.ForeignKey(WatchType, on_delete=models.PROTECT, related_name="products")
    strap_type = models.ForeignKey(StrapType, on_delete=models.PROTECT, related_name="products")
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=220,unique=True, null=True, blank=True)
    color = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product"
        ordering = ["-created_at"]

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first()
        
    def save(self, *args, **kwargs):
        if not self.product_id:
            while True:
                code = generate_code("PRD", 6)

                if not Products.objects.filter(
                    product_id=code
                ).exists():
                    self.product_id = code
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_id} - {self.name}"

class ProductImage(BaseModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "product_image"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"{self.product.product_id} - Image"
