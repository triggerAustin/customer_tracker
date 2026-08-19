from django.db import models


class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    physical_address = models.TextField(blank=True)
    national_id_number = models.CharField(max_length=20, unique=True)
    kra_pin = models.CharField(max_length=20, blank=True)
    date_registered = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name
