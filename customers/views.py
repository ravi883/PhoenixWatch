from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import CustomerSignupForm, CustomerLoginForm, ProfileUpdateForm, ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm
from django.contrib.auth.hashers import check_password, make_password
from .models import Customer
from banners.models import Banner, Headline
from products.models import *
from itertools import chain
from cart.models import *
from decimal import Decimal, ROUND_HALF_UP
from .tokens import customer_password_reset_token
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from order.models import Coupon


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

# def forgot_password_view(request):
#     return render(request, "forgot_password.html")

def checkout_view(request):
    ## GET Customer
    customer_id = request.session.get("customer_id")
    if not customer_id:
        messages.warning(request, "Please login before proceeding to checkout.")
        return redirect("login")

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        request.session.pop("customer_id", None)
        messages.error(request, "Customer account not found.")
        return redirect("login")

    ##GET Cart
    cart = Cart.objects.filter(customer=customer).first()
    if not cart:
        messages.warning(request,"Your cart is empty.")
        return redirect("cart")

    ##GET Cart Items
    cart_items = (CartItem.objects.filter(cart=cart).select_related("product","product__category","product__watch_type","product__strap_type"))
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    ##CALCULATE SUBTOTAL 
    subtotal = cart.subtotal

    ## COUPON CODE
    if request.method== "POST":
        coupon = request.POST.get("coupon")
        if not coupon:
            messages.warning(request, "Enter Coupon Code.",extra_tags="coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        coupon_obj = Coupon.objects.filter(coupon_code__iexact=coupon)
        
        if not coupon_obj:
            messages.warning(request, "Invalid Coupon.",extra_tags="coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart.coupon:
            messages.warning(request, "Coupon already exists.",extra_tags="coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not cart.subtotal > coupon_obj.first().minimum_order_amount:
            messages.warning(request,f"Amount should be greater than {coupon_obj.first().minimum_order_amount}",extra_tags="coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if coupon_obj.first().is_expired:
            messages.warning(request, "Coupon Expired.",extra_tags="coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart.coupon = coupon_obj[0]
        cart.coupon_code = coupon
        cart.discount_amount = cart.discount_price
        cart.save()

        messages.success(request, "Coupon applied.",extra_tags="coupon")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

    advance_amount = (cart.subtotal * Decimal("0.20")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    remaining_amount = (cart.subtotal - advance_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    context = {
        "customer": customer,
        "cart": cart,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "advance_amount": str(advance_amount),
        "remaining_amount": str(remaining_amount),
    }
    return render(request, "checkout.html", context)

def cart_view(request):
    return render(request, "cart.html")

def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():

            email = form.cleaned_data["email"]
            customer = Customer.objects.filter(email__iexact=email).first()

            # Same response whether customer exists or not.
            if customer:
                token = customer_password_reset_token.make_token(customer)

                uid = force_bytes(customer.pk)
                uid_encoded = urlsafe_base64_encode(uid)

                reset_url = request.build_absolute_uri(
                    reverse("reset-password",
                        kwargs={
                            "uidb64": uid_encoded,
                            "token": token,
                        },
                    )
                )
                
                expiry_minutes = 30
                context = {
                    "customer": customer,
                    "reset_url": reset_url,
                    "expiry_minutes": expiry_minutes,
                }

                subject = "Reset your PhoenixWatch password"

                text_content = render_to_string("emails/password_reset.txt", context)

                html_content = render_to_string("emails/password_reset.html", context)

                email_message = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[customer.email],
                )

                email_message.attach_alternative(html_content,"text/html")
                email_message.send(fail_silently=False)

            messages.success(request,"If an account exists with that email, " "you will receive a password reset link shortly.")
            return redirect("forgot_password")

    else:
        form = ForgotPasswordForm()

    return render(
        request,
        "forgot_password.html",
        {"form": form},
    )

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        customer = Customer.objects.get(pk=uid)

    except (
        TypeError,
        ValueError,
        OverflowError,
        Customer.DoesNotExist,
    ):
        customer = None

    if customer is None:
        messages.error( request,"This password reset link is invalid.")
        return redirect("forgot-password")

    token_valid = customer_password_reset_token.check_token( customer, token)

    if not token_valid:
        messages.error(request,"This password reset link is invalid or has expired.")
        return redirect("forgot-password")

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["password"]
            customer.password = make_password(new_password)
            customer.save(update_fields=["password"])

            messages.success(request, "Your password has been reset successfully. " "You can now login.")
            return redirect("login")

    else:
        form = ResetPasswordForm()

    return render(request,"reset_password.html",{ "form": form, "customer": customer},
    )


def remove_coupon_view(request, cart_id):
    cart = Cart.objects.get(id=cart_id)
    cart.coupon = None
    cart.coupon_code = ''
    cart.discount_amount = cart.discount_price
    cart.save()

    messages.success(request, "Coupon Removed.",extra_tags="coupon")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
