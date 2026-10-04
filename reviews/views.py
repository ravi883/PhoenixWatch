from django.contrib import messages
from django.db import transaction
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from customers.models import Customer
from products.models import Products

from .forms import ProductReviewForm, validate_review_images
from .models import ProductReview, ProductReviewImage
from order.models import OrderItem

# Create your views here.

def product_review(request, slug):
    product = get_object_or_404(
            Products.objects.prefetch_related("images"),
            slug=slug,
            is_active=True
        )
    
    return render(request, "product-review.html",{"product":product})

def customer_purchased_product(customer, product):

    return OrderItem.objects.filter(
        order__customer=customer,
        product=product,
        order__status="delivered"
    ).exists()

def add_review(request, product_id):
    product = get_object_or_404(
            Products.objects.prefetch_related("images"),
            product_id= product_id,
            is_active=True
            )
        
    if request.method != "POST":
        return redirect("product_review",slug=product.slug)

    # -----------------------------------
    # Check customer login
    # -----------------------------------

    customer_id = request.session.get("customer_id")

    if not customer_id:
        messages.error(request,"Please login to write a review.", extra_tags="error")

        return redirect("product_review",slug=product.slug)

    customer = get_object_or_404(Customer,id=customer_id)
    product = get_object_or_404(Products, slug=product.slug)

    # -----------------------------------
    # Prevent duplicate review
    # -----------------------------------

    if ProductReview.objects.filter(product=product,customer=customer).exists():
        messages.warning( request,"You have already reviewed this product.",extra_tags="warning")
        return redirect("product_review", slug=product.slug)

    # -----------------------------------
    # Form
    # -----------------------------------

    form = ProductReviewForm(request.POST)
    images = request.FILES.getlist("review_images")
    print(form.is_valid)
    if not form.is_valid():
        messages.error(request,"Please enter a valid rating, title and review." ,extra_tags="error")
        return redirect("product_review", slug=product.slug)
    
    # -----------------------------------
    # Validate images
    # -----------------------------------

    try:
        validate_review_images(images)
    except Exception as e:
        messages.error(request,str(e), extra_tags="error")
        return redirect("product_review", slug=product.slug)

    # -----------------------------------
    # Create review
    # -----------------------------------

    is_verified_purchase = customer_purchased_product(customer,product)
    try:
        with transaction.atomic():

            review = form.save(commit=False)
            review.product = product
            review.customer = customer

            # We'll determine this properly later
            review.is_verified_purchase = is_verified_purchase
            review.save()

            # -----------------------------------
            # Save images
            # -----------------------------------

            for image in images:

                ProductReviewImage.objects.create(review=review,image=image)

        messages.success( request, "Your review has been submitted successfully", extra_tags="success")
    except Exception as e:

        messages.error(request,"Something went wrong while submitting your review.", extra_tags="error")

    return redirect("product_review", slug=product.slug)
