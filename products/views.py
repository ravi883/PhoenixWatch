from django.shortcuts import get_object_or_404, render

from .models import Products

# Create your views here.
def product_detail_view(request, slug):

    product = get_object_or_404(
        Products.objects.prefetch_related("images"),
        slug=slug,
        is_active=True
    )
    print("product: ",product)
    return render(
        request,
        "product-detail.html",
        {
            "product": product,
        }
    )