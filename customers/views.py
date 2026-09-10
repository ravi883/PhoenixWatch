from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import CustomerSignupForm, CustomerLoginForm, ProfileUpdateForm, ChangePasswordForm
from django.contrib.auth.hashers import check_password, make_password
from .models import Customer
from banners.models import Banner, Headline
from products.models import *
from itertools import chain

def signup(request):
    if request.method == "POST":
        form = CustomerSignupForm(request.POST)

        if form.is_valid():
            customer = form.save()
            # messages.success(request, "Account created successfully! You can now login.")
            return redirect('/customers/login/')
    else:
        form = CustomerSignupForm()
    return render(request,"signup.html",{"form": form})

def login_view(request):

    if request.method == "POST":
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            customer = form.customer
            # Store customer ID in session
            request.session["customer_id"] = customer.id
            # messages.success(request, "Login successful.")
            return redirect("home")
    else:
        form = CustomerLoginForm()
    return render(request, "login.html",{ "form": form })

def home_view(request):
    banners = Banner.objects.filter(is_active=True).order_by('id')
    headlines = Headline.objects.filter(is_active=True)

    watch_types = WatchType.objects.filter(is_active=True).order_by("created_at")
    strap_types = StrapType.objects.filter(is_active=True).order_by('created_at')

    best_sellers = Products.objects.filter(
        is_active=True
    ).order_by('-updated_at')[:4].prefetch_related("images")

    categories = []
    
    for category in watch_types:
        category.category_type = "watch"
        categories.append(category)

    for category in strap_types:
        category.category_type = "strap"
        categories.append(category)

    # Only first 5 for homepage
    home_categories = categories[:5]

    return render(request, "home.html",{ "banners": banners , 'headlines' : headlines, "categories": home_categories,"best_sellers": best_sellers,})

def logout_view(request):
    if request.session.keys():  
        request.session.flush()
        return redirect("login")
    else:
        return redirect("login")

def profile_view(request):
    customer_id = request.session.get("customer_id")

    if not customer_id:
        messages.error(request, "Please login first.")
        return redirect("login")

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        request.session.flush()
        messages.error(request, "Customer account not found.",extra_tags="profile")
        return redirect("login")

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=customer)

        if form.is_valid():
            changed_fields = form.changed_data
            if changed_fields:
                customer.save(
                    update_fields=changed_fields
                )
                messages.success(
                    request,
                    "Profile updated successfully.",extra_tags="profile"
                )

            else:
                messages.info(
                    request,
                    "No changes were made.",extra_tags="profile"
                )

            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=customer)

    return render(request,"profile.html",
        {
            "form": form,
            "customer": customer,
            
        }
    )
    
def change_password_view(request):
    customer_id = request.session.get("customer_id")

    if not customer_id:
        messages.error(request, "Please login first.")
        return redirect("login")

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        request.session.flush()
        messages.error(request, "Customer account not found.")
        return redirect("login")

    if request.method == "POST":
        password_form = ChangePasswordForm(request.POST,customer=customer)

        if password_form.is_valid():
            new_password = password_form.cleaned_data["new_password"]

            # Hash password
            customer.password = make_password(new_password)

            customer.save(update_fields=["password"])

            messages.success(
                request,
                "Password changed successfully.",extra_tags="change_password"
            )
            return redirect("logout")

    else:
        password_form = ChangePasswordForm(
            customer=customer
        )
    return render(
        request,
        "profile.html",
        {
            "form": password_form,
            "customer": customer,
        }
    )

def forgot_password_view(request):
    return render(request, "forgot_password.html")

def checkout_view(request):
    return render(request, "checkout.html")

def cart_view(request):
    return render(request, "cart.html")