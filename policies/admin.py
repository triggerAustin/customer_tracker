from django.contrib import admin

from .models import Beneficiary, Insurer, Payment, Policy, PolicyType, PremiumSchedule


@admin.register(PolicyType)
class PolicyTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Insurer)
class InsurerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_phone", "contact_email")
    search_fields = ("name",)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class PremiumScheduleInline(admin.TabularInline):
    model = PremiumSchedule
    extra = 0


class BeneficiaryInline(admin.TabularInline):
    model = Beneficiary
    extra = 0


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "policy_number",
        "customer",
        "policy_type",
        "insurer",
        "status",
        "expiry_date",
    )
    list_filter = ("status", "policy_type", "insurer")
    search_fields = ("policy_number", "customer__full_name")
    inlines = [PaymentInline, PremiumScheduleInline, BeneficiaryInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("policy", "amount_paid", "date_paid", "payment_method")
    list_filter = ("payment_method",)
    search_fields = ("policy__policy_number", "reference_number")


@admin.register(PremiumSchedule)
class PremiumScheduleAdmin(admin.ModelAdmin):
    list_display = ("policy", "amount_due", "due_date", "status")
    list_filter = ("status",)
    search_fields = ("policy__policy_number",)


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "policy", "relationship_to_policyholder", "percentage_share")
    search_fields = ("full_name", "policy__policy_number")
