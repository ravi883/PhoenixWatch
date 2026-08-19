from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import CustomerSignupForm, CustomerLoginForm
from django.contrib.auth.hashers import check_password
from .models import Customer

def signup(request):
    if request.method == "POST":
        form = CustomerSignupForm(request.POST)
        
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Account created successfully! You can now login.")
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
            messages.success(request, "Login successful.")
            return redirect("home")
    else:
        form = CustomerLoginForm()
    return render(request, "login.html",{ "form": form })

def home_view(request):
    return render(request,'home.html')