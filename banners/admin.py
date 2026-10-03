from django.contrib import admin
from .models import Banner, Headline

# Register your models here.
@admin.register(Banner)
class BannersAdmin(admin.ModelAdmin):
    list_display=['id','image', 'is_active','created_at']


@admin.register(Headline)
class HeadlineAdmin(admin.ModelAdmin):
    list_display=['id','description', 'is_active','created_at']