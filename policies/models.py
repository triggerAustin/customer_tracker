from django.db import models

from customers.models import Customer


class PolicyType(models.Model):
    """Open-ended lookup table — staff can add new types freely."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Insurer(models.Model):
    """The actual insurance company backing a policy (agency brokers for several)."""

    name = models.CharField(max_length=255, unique=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Policy(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        LAPSED = "lapsed", "Lapsed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    class PremiumFrequency(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUALLY = "annually", "Annually"

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="policies"
    )
    policy_type = models.ForeignKey(
        PolicyType, on_delete=models.PROTECT, related_name="policies"
    )
    insurer = models.ForeignKey(
        Insurer, on_delete=models.PROTECT, related_name="policies"
    )
    policy_number = models.CharField(max_length=100, unique=True)
    coverage_amount = models.DecimalField(max_digits=14, decimal_places=2)
    premium_amount = models.DecimalField(max_digits=14, decimal_places=2)
    premium_frequency = models.CharField(
        max_length=20, choices=PremiumFrequency.choices
    )
    start_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name_plural = "policies"

    def __str__(self):
        return f"{self.policy_number} ({self.customer.full_name})"


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        MPESA = "mpesa", "M-Pesa"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CHEQUE = "cheque", "Cheque"

    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, related_name="payments"
    )
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2)
    date_paid = models.DateField()
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    reference_number = models.CharField(max_length=100, blank=True)
    period_covered = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_paid"]

    def __str__(self):
        return f"{self.policy.policy_number} - {self.amount_paid} on {self.date_paid}"


class PremiumSchedule(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, related_name="premium_schedule"
    )
    amount_due = models.DecimalField(max_digits=14, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.policy.policy_number} due {self.due_date}"


class Beneficiary(models.Model):
    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, related_name="beneficiaries"
    )
    full_name = models.CharField(max_length=255)
    relationship_to_policyholder = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20, blank=True)
    percentage_share = models.DecimalField(max_digits=5, decimal_places=2)
    contact_info = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["policy", "-percentage_share"]
        verbose_name_plural = "beneficiaries"

    def __str__(self):
        return f"{self.full_name} ({self.percentage_share}% of {self.policy.policy_number})"
