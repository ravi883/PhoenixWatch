from django import forms
from PIL import Image
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):

    class Meta:
        model = ProductReview

        fields = ["rating","title","description", "display_name"]

        widgets = {
            "rating": forms.HiddenInput(),

            "title": forms.TextInput(
                attrs={
                    "placeholder": "Write a short title",
                    "maxlength": "150",
                    "class": "w-full",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "Tell us about your experience...",
                    "rows": 5,
                    "maxlength": "2000",
                    "class": "w-full",
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")

        if rating is None:
            raise forms.ValidationError("Please select a rating.")

        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5 stars.")

        return rating

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()

        if not title:
            raise forms.ValidationError( "Please enter a review title.")

        return title

    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()

        if not description:
            raise forms.ValidationError("Please enter your review.")

        return description

    def clean_display_name(self):
        display_name = self.cleaned_data.get("display_name", "").strip()

        if not display_name:
            raise forms.ValidationError( "Please enter a display name.")

        return display_name

def validate_review_images(files):
    max_images = 5
    max_size = 5 * 1024 * 1024  # 5 MB

    if len(files) > max_images:
        raise forms.ValidationError(
            f"You can upload a maximum of {max_images} images."
        )

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    for image in files:

        if image.content_type not in allowed_types:
            raise forms.ValidationError(
                "Only JPG, PNG and WEBP images are allowed."
            )

        if image.size > max_size:
            raise forms.ValidationError(
                "Each image must be smaller than 5 MB."
            )
        try:
            img = Image.open(image)
            img.verify()

        except Exception:
            raise forms.ValidationError(
                "Invalid image file."
            )