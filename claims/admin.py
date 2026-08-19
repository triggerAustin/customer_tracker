from django.contrib import admin

from .models import Claim, ClaimStatusHistory


class ClaimStatusHistoryInline(admin.TabularInline):
    model = ClaimStatusHistory
    extra = 0
    readonly_fields = ("date_changed",)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "date_filed",
        "amount_claimed",
        "amount_approved",
        "current_status",
    )
    list_filter = ("current_status",)
    search_fields = ("policy__policy_number", "description")
    inlines = [ClaimStatusHistoryInline]


@admin.register(ClaimStatusHistory)
class ClaimStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("claim", "status", "date_changed")
    list_filter = ("status",)
    search_fields = ("claim__policy__policy_number",)
