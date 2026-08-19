from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "national_id_number", "date_registered")
    search_fields = ("full_name", "phone_number", "national_id_number", "kra_pin")
    list_filter = ("date_registered",)
