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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False

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

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()

        changed_fields = self.changed_data

        if "first_name" in changed_fields:

            first_name = cleaned_data.get("first_name", "").strip()

            if not first_name:
                self.add_error(
                    "first_name",
                    "First name is required."
                )

            elif len(first_name) < 2:
                self.add_error(
                    "first_name",
                    "First name must contain at least 2 characters."
                )

            elif not re.fullmatch(r"[A-Za-z ]+", first_name):
                self.add_error(
                    "first_name",
                    "First name can contain only letters."
                )

        if "last_name" in changed_fields:

            last_name = cleaned_data.get("last_name", "").strip()

            if not last_name:
                self.add_error(
                    "last_name",
                    "Last name is required."
                )

            elif len(last_name) < 2:
                self.add_error(
                    "last_name",
                    "Last name must contain at least 2 characters."
                )

            elif not re.fullmatch(r"[A-Za-z ]+", last_name):
                self.add_error(
                    "last_name",
                    "Last name can contain only letters."
                )

        if "email" in changed_fields:

            email = cleaned_data.get("email", "").strip().lower()

            if not email:
                self.add_error(
                    "email",
                    "Email is required."
                )

            else:

                try:
                    validate_email(email)

                except ValidationError:
                    self.add_error(
                        "email",
                        "Enter a valid email address."
                    )

                if Customer.objects.filter(
                    email__iexact=email
                ).exclude(
                    pk=self.instance.pk
                ).exists():

                    self.add_error(
                        "email",
                        "This email address is already registered."
                    )

        if "phone_number" in changed_fields:

            phone = cleaned_data.get(
                "phone_number",
                ""
            ).strip()

            if not phone:
                self.add_error(
                    "phone_number",
                    "Phone number is required."
                )

            elif not re.fullmatch(
                r"[0-9]{10}",
                phone
            ):
                self.add_error(
                    "phone_number",
                    "Phone number must contain exactly 10 digits."
                )

            elif phone[0] not in "6789":
                self.add_error(
                    "phone_number",
                    "Enter a valid Indian mobile number."
                )

            elif Customer.objects.filter(
                phone_number=phone
            ).exclude(
                pk=self.instance.pk
            ).exists():

                self.add_error(
                    "phone_number",
                    "This phone number is already registered."
                )

        if "city" in changed_fields:

            city = cleaned_data.get("city", "").strip()

            if not city:
                self.add_error(
                    "city",
                    "City is required."
                )

            elif not re.fullmatch(
                r"[A-Za-z ]+",
                city
            ):
                self.add_error(
                    "city",
                    "City can contain only letters."
                )

        if "state" in changed_fields:

            state = cleaned_data.get("state", "").strip()

            if not state:
                self.add_error(
                    "state",
                    "State is required."
                )

            elif not re.fullmatch(
                r"[A-Za-z ]+",
                state
            ):
                self.add_error(
                    "state",
                    "State can contain only letters."
                )

        if "country" in changed_fields:

            country = cleaned_data.get("country", "").strip()

            if not country:
                self.add_error(
                    "country",
                    "Country is required."
                )

            elif not re.fullmatch(
                r"[A-Za-z ]+",
                country
            ):
                self.add_error(
                    "country",
                    "Country can contain only letters."
                )

        if "pincode" in changed_fields:

            pincode = cleaned_data.get(
                "pincode",
                ""
            ).strip()

            if not re.fullmatch(
                r"[0-9]{6}",
                pincode
            ):
                self.add_error(
                    "pincode",
                    "Pincode must contain exactly 6 digits."
                )

        return cleaned_data


class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(label="current_password",widget=forms.PasswordInput())
    new_password = forms.CharField(label="new_password",widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="confirm_password",widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop("customer", None)
        super().__init__(*args, **kwargs)


    def clean_current_password(self):

        current_password = self.cleaned_data.get(
            "current_password"
        )

        if not current_password:
            return current_password

        if not self.customer:
            raise forms.ValidationError(
                "Customer account could not be found."
            )

        if not check_password(
            current_password,
            self.customer.password
        ):
            raise forms.ValidationError(
                "Current password is incorrect."
            )

        return current_password

    # -------------------------------
    # New password validation
    # -------------------------------

    def clean_new_password(self):

        new_password = self.cleaned_data.get(
            "new_password"
        )

        if not new_password:
            return new_password

        # Minimum length
        if len(new_password) < 8:
            raise forms.ValidationError(
                "Password must contain at least 8 characters."
            )

        # Maximum length
        if len(new_password) > 128:
            raise forms.ValidationError(
                "Password cannot exceed 128 characters."
            )

        # Uppercase
        if not re.search(
            r"[A-Z]",
            new_password
        ):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        # Lowercase
        if not re.search(
            r"[a-z]",
            new_password
        ):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        # Number
        if not re.search(
            r"\d",
            new_password
        ):
            raise forms.ValidationError(
                "Password must contain at least one number."
            )

        # Special character
        if not re.search(
            r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\];'`~]",
            new_password
        ):
            raise forms.ValidationError(
                "Password must contain at least one special character."
            )

        # Prevent same password
        if self.customer:

            if check_password(
                new_password,
                self.customer.password
            ):
                raise forms.ValidationError(
                    "New password must be different from your current password."
                )

        return new_password

    # -------------------------------
    # Confirm password validation
    # -------------------------------

    def clean_confirm_password(self):

        confirm_password = self.cleaned_data.get(
            "confirm_password"
        )

        new_password = self.cleaned_data.get(
            "new_password"
        )

        if (
            confirm_password
            and new_password
            and confirm_password != new_password
        ):
            raise forms.ValidationError(
                "New password and confirm password do not match."
            )

        return confirm_password