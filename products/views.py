from django.shortcuts import get_object_or_404, render

from .models import Products
from reviews.models import ProductReview, ProductReviewImage
from django.core.paginator import Paginator
from django.db.models import Avg

# Create your views here.
def product_detail_view(request, slug):

    product = get_object_or_404(
        Products.objects.prefetch_related("images"),
        slug=slug,
        is_active=True
    )

    recomend_products = Products.objects.filter(
            is_active=True
        ).order_by('-updated_at')[:4].prefetch_related("images")

    base_reviews  = ProductReview.objects.filter(
        product=product,
        is_approved=True
    )

    # ---------------------------------------
    # Filter counts
    # ---------------------------------------
    
    all_reviews_count = base_reviews.count()

    rating_counts = {
        5: base_reviews.filter(rating=5).count(),
        4: base_reviews.filter(rating=4).count(),
        3: base_reviews.filter(rating=3).count(),
        2: base_reviews.filter(rating=2).count(),
        1: base_reviews.filter(rating=1).count(),
    }

    # Rating percentages
    rating_percentages = {}

    for rating in range(1, 6):
        count = rating_counts[rating]

        if all_reviews_count > 0:
            percentage = round((count / all_reviews_count) * 100, 1)
        else:
            percentage = 0

        rating_percentages[rating] = percentage


    photo_reviews_count = base_reviews.filter(
        images__isnull=False
    ).distinct().count()

    average_rating = base_reviews.aggregate(
        average=Avg("rating")
    )["average"] or 0

    five_star_reviews_count = rating_counts[5]

    reviews = base_reviews.prefetch_related(
        "images"
    ).order_by(
        "-created_at"
    )

    # ---------------------------------------
    # Selected filter
    # ---------------------------------------

    selected_filter = request.GET.get("filter", "all")


    if selected_filter == "photos":

        reviews = reviews.filter(
            images__isnull=False
        ).distinct()

    elif selected_filter == "five-star":

        reviews = reviews.filter(
            rating=5
        )


    # ---------------------------------------
    # Pagination
    # ---------------------------------------

    paginator = Paginator(reviews,4)

    page_number = request.GET.get("page")

    reviews_page = paginator.get_page(page_number)
    
    return render(
        request,
        "product-detail.html",
        {
            "product": product,
            "recomend_products": recomend_products,
            "reviews": reviews,
             # Paginated reviews
            "reviews": reviews_page,

            # Counts
            "all_reviews_count": all_reviews_count,
            "photo_reviews_count": photo_reviews_count,
            "five_star_reviews_count": five_star_reviews_count,
            "rating_counts": rating_counts,
            "rating_percentages": rating_percentages,
            "average_rating":round(average_rating, 1),

            # Current filter
            "selected_filter": selected_filter,
        }
    )