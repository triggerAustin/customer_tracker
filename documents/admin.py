from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "document_type",
        "customer",
        "policy",
        "claim",
        "date_uploaded",
    )
    list_filter = ("document_type",)
    search_fields = (
        "description",
        "customer__full_name",
        "policy__policy_number",
    )
    readonly_fields = ("date_uploaded",)
