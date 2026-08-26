from django.shortcuts import render

# Create your views here.
def mens_collection_view(request):
    return render(request,'mens-collection.html')