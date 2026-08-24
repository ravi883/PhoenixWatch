from django.db import models
from customers.models import BaseModel

# Create your models here.

class Banner(BaseModel):
    image = models.ImageField(upload_to="banners/")
    title = models.CharField(
        max_length=100,
        blank=True
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True
    )
    button_text = models.CharField(
        max_length=50,
        blank=True
    )
    button_url = models.CharField(
        max_length=255,
        blank=True
    )
    is_active = models.BooleanField(default=True)

class Headline(BaseModel):
    description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.description