from django import forms

from .models import Policy, PolicyType


class PolicyTypeForm(forms.ModelForm):
    class Meta:
        model = PolicyType
        fields = ["name", "description"]
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": "Optional"}),
        }


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = [
            "customer",
            "policy_type",
            "insurer",
            "policy_number",
            "coverage_amount",
            "premium_amount",
            "premium_frequency",
            "start_date",
            "expiry_date",
            "status",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
