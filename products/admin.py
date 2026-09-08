from django.contrib import admin
from .models import *


@admin.register(Categories)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name','slug','is_active']
    

@admin.register(WatchType)
class WatchTypeAdmin(admin.ModelAdmin):
    list_display = ['id','name','slug','is_active']


@admin.register(StrapType)
class StrapTypeAdmin(admin.ModelAdmin):
    list_display = ['id','name','slug','is_active']

# @admin.register(ProductImage)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fk_name = 'product'


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ['product_id','name','price','stock', 'is_active']

