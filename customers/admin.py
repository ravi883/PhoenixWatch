from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = ("id", "get_full_name","get_email","get_phone_number","city","state","created_at")

    list_filter = ("state", "city", "created_at")

    search_fields = ("first_name", "last_name", "email", "_phone_number", "city", "state", "pincode")

    readonly_fields = ("created_at", "updated_at")

    ordering = ("-created_at",)

    @admin.display(description="Full Name")
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Email")
    def get_email(self, obj):
        return obj.email

    @admin.display(description="Phone Number")
    def get_phone_number(self, obj):
        return obj.phone_number