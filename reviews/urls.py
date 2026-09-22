from django.urls import path

from . import views



urlpatterns = [
    path("<slug:slug>/",views.product_review, name="product_review"),
    path("add/<product_id>/", views.add_review, name="add_review"),

]