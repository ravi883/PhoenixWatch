from http.client import HTTPResponse

from django.shortcuts import get_object_or_404, render
from products.models import *
from django.core.paginator import Paginator
from itertools import chain

# Create your views here.
def mens_collection_view(request):
    mens_products = Products.objects.filter(category__slug="mens-watches", is_active=True).prefetch_related("images")

    paginator = Paginator(mens_products, 4)  # 4 products per page
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)
    
    return render(request,'mens-collection.html',{'products': products})

def all_collection_view(request):
    watch_types = WatchType.objects.filter(is_active=True).order_by("created_at")
    strap_types = StrapType.objects.filter(is_active=True).order_by('created_at')
    
    categories = []

    for category in watch_types:
        category.category_type = "watch"
        categories.append(category)

    for category in strap_types:
        category.category_type = "strap"
        categories.append(category)

    
    paginator = Paginator(categories, 9)  # 9 categories per page

    page_number = request.GET.get("page")
    categories = paginator.get_page(page_number)
    return render(request, 'collections.html',{'categories' : categories})

def category_products_view(request,slug):
    category = get_object_or_404(
        Categories,
        slug=slug,
        is_active=True
    )

    products = Products.objects.filter(
        category=category,
        is_active=True
    ).prefetch_related("images")

    return render(
        request,
        "category-products.html",
        {
            "category": category,
            "products": products,
        }
    )

def watch_type_products_view(request, slug):

    watch_type = get_object_or_404(
        WatchType,
        slug=slug,
        is_active=True
    )

    products = Products.objects.filter(
        watch_type=watch_type,
        is_active=True
    ).prefetch_related("images")

    # Get price range from URL
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Apply minimum price
    if min_price:
        try:
            products = products.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass

    # Apply maximum price
    if max_price:
        try:
            products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass

    # -------------------------
    # SORTING
    # -------------------------

    sort = request.GET.get("sort")
    if sort == "alpha-asc":
        products = products.order_by("name")

    elif sort == "alpha-desc":
        products = products.order_by("-name")

    elif sort == "price-asc":
        products = products.order_by("price")

    elif sort == "price-desc":
        products = products.order_by("-price")

    else:
        sort = "alpha-asc"
        products = products.order_by("name")

    return render(request, "watch-type-products.html",
        {
            "watch_type": watch_type,
            "products": products,
            "min_price": min_price or "",
            "max_price": max_price or "",
            "sort": sort,
        }
    )

def strap_type_products_view(request, slug):
    strap_type = get_object_or_404(
        StrapType,
        slug=slug,
        is_active=True
    )

    products = Products.objects.filter(
        strap_type=strap_type,
        is_active=True
    )

    # Get price range from URL
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Apply minimum price
    if min_price:
        try:
            products = products.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass

    # Apply maximum price
    if max_price:
        try:
            products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass

    # -------------------------
    # SORTING
    # -------------------------

    sort = request.GET.get("sort")
    if sort == "alpha-asc":
        products = products.order_by("name")

    elif sort == "alpha-desc":
        products = products.order_by("-name")

    elif sort == "price-asc":
        products = products.order_by("price")

    elif sort == "price-desc":
        products = products.order_by("-price")

    else:
        sort = "alpha-asc"
        products = products.order_by("name")

    return render(request, "strap-type-products.html",
        {
            "strap_type": strap_type,
            "products": products,
            "min_price": min_price or "",
            "max_price": max_price or "",
            "sort": sort,
        }
    )