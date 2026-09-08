
from .views import *
from django.urls import path

urlpatterns = [
    path('', all_collection_view, name='all-collection-view'),
    path('men-collection/', mens_collection_view,name ='men-collection'),
    path('category-products/<slug:slug>/',category_products_view, name='category-products-view'),
    path('watch/<slug:slug>/',watch_type_products_view, name='watch-type-products'),
    path('strap/<slug:slug>/',strap_type_products_view, name='strap_type_products'),
]