from django.core.exceptions import ValidationError
from django.db import models

from claims.models import Claim
from customers.models import Customer
from policies.models import Policy


class Document(models.Model):
    """
    A generic attachment. Exactly one of `customer`, `policy`, or `claim`
    should be set — see clean().
    """

    class DocumentType(models.TextChoices):
        ID_COPY = "id_copy", "ID Copy"
        POLICY_DOCUMENT = "policy_document", "Policy Document"
        CLAIM_EVIDENCE = "claim_evidence", "Claim Evidence"
        OTHER = "other", "Other"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="documents/%Y/%m/")
    document_type = models.CharField(
        max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER
    )
    description = models.CharField(max_length=255, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_uploaded"]

    def clean(self):
        linked = [self.customer_id, self.policy_id, self.claim_id]
        if sum(1 for value in linked if value) != 1:
            raise ValidationError(
                "A document must be linked to exactly one of: customer, policy, or claim."
            )

    def __str__(self):
        target = self.customer or self.policy or self.claim
        return f"{self.get_document_type_display()} - {target}"
