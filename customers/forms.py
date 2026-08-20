from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "full_name",
            "phone_number",
            "email",
            "physical_address",
            "national_id_number",
            "kra_pin",
            "notes",
        ]
        widgets = {
            "physical_address": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
