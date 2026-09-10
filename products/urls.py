from django.urls import path
from .views import *

urlpatterns = [
    path("<slug:slug>/", product_detail_view, name="product-detail"),
]