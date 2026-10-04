from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from customers.models import Customer
from products.models import Products
from order.models import BaseModel


class ProductReview(BaseModel):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name="reviews")
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name="product_reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=2000)
    display_name = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "customer"],
                name="unique_customer_product_review"
            )
        ]

    def __str__(self):
        return f"{self.product} - {self.customer} - {self.rating}★"


class ProductReviewImage(BaseModel):
    review = models.ForeignKey(ProductReview,on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to="reviews/")


    def __str__(self):
        return f"Image for Review #{self.review.id}"