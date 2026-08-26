
from .views import mens_collection_view
from django.urls import path

urlpatterns = [
    path('men-collection/',mens_collection_view,name ='men-collection')
]