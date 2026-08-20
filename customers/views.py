from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerForm
from .models import Customer


def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "customers/customer_list.html", {"customers": customers})


def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    policies = customer.policies.select_related("policy_type", "insurer").all()
    return render(
        request,
        "customers/customer_detail.html",
        {"customer": customer, "policies": policies},
    )


def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f"Customer {customer.full_name} created.")
            return redirect("customers:customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()
    return render(
        request, "customers/customer_form.html", {"form": form, "mode": "create"}
    )


def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer {customer.full_name} updated.")
            return redirect("customers:customer_detail", pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(
        request,
        "customers/customer_form.html",
        {"form": form, "mode": "edit", "customer": customer},
    )
