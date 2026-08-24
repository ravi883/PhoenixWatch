from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import CustomerSignupForm, CustomerLoginForm, ProfileUpdateForm, ChangePasswordForm
from django.contrib.auth.hashers import check_password, make_password
from .models import Customer
from django.contrib.auth.decorators import login_required
from banners.models import Banner, Headline

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
    print(banners)
    headlines = Headline.objects.filter(is_active=True)
    return render(request, "home.html",{ "banners": banners , 'headlines' : headlines})

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
