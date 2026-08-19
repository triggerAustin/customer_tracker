from django.db import models

from policies.models import Policy


class Claim(models.Model):
    class Status(models.TextChoices):
        FILED = "filed", "Filed"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        PAID = "paid", "Paid"

    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, related_name="claims"
    )
    date_filed = models.DateField()
    description = models.TextField()
    amount_claimed = models.DecimalField(max_digits=14, decimal_places=2)
    amount_approved = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    current_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.FILED
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_filed"]

    def __str__(self):
        return f"Claim on {self.policy.policy_number} filed {self.date_filed}"


class ClaimStatusHistory(models.Model):
    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.CharField(max_length=20, choices=Claim.Status.choices)
    date_changed = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_changed"]
        verbose_name_plural = "claim status history"

    def __str__(self):
        return f"{self.claim} -> {self.status} on {self.date_changed}"
