from django.contrib import admin

from .models import ProductReview, ProductReviewImage


class ProductReviewImageInline(
    admin.TabularInline
):
    model = ProductReviewImage
    extra = 0


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "customer",
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )

    search_fields = (
        "product__name",
        "customer__email",
        "title",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [
        ProductReviewImageInline
    ]


@admin.register(ProductReviewImage)
class ProductReviewImageAdmin(admin.ModelAdmin):

    list_display = (
        "review",
        "created_at",
    )