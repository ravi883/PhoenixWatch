import re

from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.hashers import check_password

from .models import Customer


class CustomerSignupForm(forms.ModelForm):

    password = forms.CharField(label="Password",widget=forms.PasswordInput())

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone_number", "password"]

    def clean_first_name(self):
        first_name = self.cleaned_data.get(
            "first_name",
            ""
        ).strip()

        if not first_name:
            raise forms.ValidationError(
                "First name is required."
            )

        if len(first_name) < 2:
            raise forms.ValidationError(
                "First name must contain at least 2 characters."
            )

        if not re.match(
            r"^[A-Za-z\s]+$",
            first_name
        ):

            raise forms.ValidationError(
                "First name can contain only letters and spaces."
            )

        return first_name

    def clean_last_name(self):

        last_name = self.cleaned_data.get(
            "last_name",
            ""
        ).strip()

        if not last_name:
            raise forms.ValidationError(
                "Last name is required."
            )

        if len(last_name) < 2:
            raise forms.ValidationError(
                "Last name must contain at least 2 characters."
            )

        if not re.match(
            r"^[A-Za-z\s]+$",
            last_name
        ):
            raise forms.ValidationError(
                "Last name can contain only letters and spaces."
            )

        return last_name

    def clean_email(self):

        email = self.cleaned_data.get(
            "email",
            ""
        ).strip().lower()

        if not email:
            raise forms.ValidationError(
                "Email address is required."
            )

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError(
                "Please enter a valid email address."
            )

        if Customer.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_phone_number(self):

        phone_number = self.cleaned_data.get(
            "phone_number",
            ""
        ).strip()

        # Remove spaces, + and -
        phone_number = re.sub(
            r"[\s\-+]",
            "",
            phone_number
        )

        if not phone_number:
            raise forms.ValidationError(
                "Phone number is required."
            )

        if not phone_number.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only digits."
            )

        # Indian 10 digit number
        if len(phone_number) != 10:
            raise forms.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        if phone_number[0] not in "6789":
            raise forms.ValidationError(
                "Please enter a valid phone number."
            )

        if Customer.objects.filter(
            phone_number=phone_number
        ).exists():

            raise forms.ValidationError(
                "An account with this phone number already exists."
            )

        return phone_number

    def clean_password(self):

        password = self.cleaned_data.get(
            "password"
        )

        if not password:
            raise forms.ValidationError(
                "Password is required."
            )

        if len(password) < 8:
            raise forms.ValidationError(
                "Password must contain at least 8 characters."
            )

        if len(password) > 12:
            raise forms.ValidationError(
                "Password cannot exceed 12 characters."
            )

        password_rules = [
        (
            r"[A-Z]",
            "Password must contain at least one uppercase letter."
        ),
        (
            r"[a-z]",
            "Password must contain at least one lowercase letter."
        ),
        (
            r"\d",
            "Password must contain at least one number."
        ),
        (
            r"[!@#$%^&*(),.?\":{}|<>_\-]",
            "Password must contain at least one special character."
        ),
        ]

        for pattern, error_message in password_rules:

            if not re.search(pattern, password):

                raise forms.ValidationError(
                error_message
             )
        return password

class CustomerLoginForm(forms.Form):

    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Password",widget=forms.PasswordInput())

    def clean_email(self):

        email = self.cleaned_data.get("email", "").strip().lower()
        customer = Customer.objects.filter(email__iexact=email).first()

        if not customer:
            raise forms.ValidationError(
                "No account found with this email address."
            )

        # Store customer so we don't query again
        self.customer = customer
        return email

    def clean_password(self):

        password = self.cleaned_data.get("password", "").strip()
        if not password:
            raise forms.ValidationError("Password is required.")
        return password

    def clean(self):

        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        # Stop if email/password already has an error
        if not email or not password:
            return cleaned_data

        # Customer was already found in clean_email()
        customer = getattr(self, "customer", None)

        if not customer:
            return cleaned_data

        # Check password
        if not check_password(
            password,
            customer.password
        ):
            self.add_error(
                "password",
                "Incorrect password."
            )

            return cleaned_data

        return cleaned_data