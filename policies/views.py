from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PolicyForm, PolicyTypeForm
from .models import Policy, PolicyType


def policy_list(request):
    policies = Policy.objects.select_related("customer", "policy_type", "insurer").all()
    return render(request, "policies/policy_list.html", {"policies": policies})


def policy_detail(request, pk):
    policy = get_object_or_404(
        Policy.objects.select_related("customer", "policy_type", "insurer"), pk=pk
    )
    context = {
        "policy": policy,
        "payments": policy.payments.all(),
        "schedule": policy.premium_schedule.all(),
        "beneficiaries": policy.beneficiaries.all(),
        "claims": policy.claims.all(),
    }
    return render(request, "policies/policy_detail.html", context)


def policy_create(request):
    if request.method == "POST":
        form = PolicyForm(request.POST)
        if form.is_valid():
            policy = form.save()
            messages.success(request, f"Policy {policy.policy_number} created.")
            return redirect("policies:policy_detail", pk=policy.pk)
    else:
        form = PolicyForm()
    return render(
        request, "policies/policy_form.html", {"form": form, "mode": "create"}
    )


def policy_edit(request, pk):
    policy = get_object_or_404(Policy, pk=pk)
    if request.method == "POST":
        form = PolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, f"Policy {policy.policy_number} updated.")
            return redirect("policies:policy_detail", pk=policy.pk)
    else:
        form = PolicyForm(instance=policy)
    return render(
        request,
        "policies/policy_form.html",
        {"form": form, "mode": "edit", "policy": policy},
    )


def policy_type_quick_add(request):
    """
    HTMX endpoint for adding a PolicyType inline.
    Used from both the New/Edit Policy form and the Policies list page.

    `context` tells us where the request came from:
      - "form": on success, refresh the <select> on the policy form (OOB swap)
      - "list": on success, just show a small confirmation message
    """
    context_source = request.GET.get("context") or request.POST.get("context") or "form"

    if request.method == "POST":
        form = PolicyTypeForm(request.POST)
        if form.is_valid():
            new_type = form.save()
            if context_source == "list":
                return render(
                    request,
                    "policies/partials/policy_type_added_confirmation.html",
                    {"new_type": new_type},
                )
            policy_types = PolicyType.objects.all()
            return render(
                request,
                "policies/partials/policy_type_select.html",
                {"policy_types": policy_types, "selected_pk": new_type.pk},
            )
        # Invalid: re-show the mini form with errors, still targeting the add area.
        return render(
            request,
            "policies/partials/policy_type_quick_add_form.html",
            {"form": form, "context_source": context_source},
        )

    form = PolicyTypeForm()
    return render(
        request,
        "policies/partials/policy_type_quick_add_form.html",
        {"form": form, "context_source": context_source},
    )


