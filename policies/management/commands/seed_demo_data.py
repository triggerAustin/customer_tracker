import datetime
import random

from django.core.management.base import BaseCommand

from claims.models import Claim, ClaimStatusHistory
from customers.models import Customer
from policies.models import Beneficiary, Insurer, Payment, Policy, PolicyType, PremiumSchedule


class Command(BaseCommand):
    help = "Seeds the database with realistic mock data for development/testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing demo data (customers, policies, etc.) before seeding.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Clearing existing data...")
            Claim.objects.all().delete()
            Beneficiary.objects.all().delete()
            PremiumSchedule.objects.all().delete()
            Payment.objects.all().delete()
            Policy.objects.all().delete()
            Insurer.objects.all().delete()
            PolicyType.objects.all().delete()
            Customer.objects.all().delete()

        today = datetime.date.today()

        # --- Policy Types ---
        type_names = ["Motor", "Health", "Life", "Property", "Travel"]
        policy_types = {}
        for name in type_names:
            pt, _ = PolicyType.objects.get_or_create(name=name)
            policy_types[name] = pt

        # --- Insurers ---
        insurer_names = ["Jubilee Insurance", "Britam", "CIC Insurance", "APA Insurance", "Madison Insurance"]
        insurers = {}
        for name in insurer_names:
            ins, _ = Insurer.objects.get_or_create(
                name=name,
                defaults={"contact_phone": "020 123 4567", "contact_email": f"info@{name.split()[0].lower()}.co.ke"},
            )
            insurers[name] = ins

        # --- Customers ---
        customer_data = [
            {
                "full_name": "Wanjiru Kamau",
                "phone_number": "+254 712 345 678",
                "email": "wanjiru.kamau@example.com",
                "physical_address": "Kilimani, Nairobi",
                "national_id_number": "23456781",
                "kra_pin": "A012345678B",
            },
            {
                "full_name": "Otieno Odhiambo",
                "phone_number": "+254 722 456 789",
                "email": "otieno.odhiambo@example.com",
                "physical_address": "Milimani, Kisumu",
                "national_id_number": "24567892",
                "kra_pin": "A023456789C",
            },
            {
                "full_name": "Amina Hassan",
                "phone_number": "+254 733 567 890",
                "email": "amina.hassan@example.com",
                "physical_address": "Nyali, Mombasa",
                "national_id_number": "25678903",
                "kra_pin": "A034567890D",
            },
            {
                "full_name": "Kiptoo Cherono",
                "phone_number": "+254 701 678 901",
                "email": "kiptoo.cherono@example.com",
                "physical_address": "Kapsoya, Eldoret",
                "national_id_number": "26789014",
                "kra_pin": "A045678901E",
            },
            {
                "full_name": "Njeri Mwangi",
                "phone_number": "+254 745 789 012",
                "email": "njeri.mwangi@example.com",
                "physical_address": "Ngong Road, Nairobi",
                "national_id_number": "27890125",
                "kra_pin": "A056789012F",
            },
        ]

        customers = []
        for data in customer_data:
            customer, _ = Customer.objects.get_or_create(
                national_id_number=data["national_id_number"], defaults=data
            )
            customers.append(customer)

        # --- Policies (a couple per customer) ---
        statuses = [Policy.Status.ACTIVE, Policy.Status.ACTIVE, Policy.Status.LAPSED, Policy.Status.EXPIRED]
        frequencies = [Policy.PremiumFrequency.MONTHLY, Policy.PremiumFrequency.QUARTERLY, Policy.PremiumFrequency.ANNUALLY]

        policies = []
        policy_counter = 1
        for customer in customers:
            for type_name in random.sample(type_names, k=2):
                policy_number = f"POL-{policy_counter:04d}"
                policy_counter += 1
                start = today - datetime.timedelta(days=random.randint(30, 400))
                expiry = start + datetime.timedelta(days=365)
                policy, _ = Policy.objects.get_or_create(
                    policy_number=policy_number,
                    defaults={
                        "customer": customer,
                        "policy_type": policy_types[type_name],
                        "insurer": random.choice(list(insurers.values())),
                        "coverage_amount": random.choice([500000, 1000000, 2500000, 5000000]),
                        "premium_amount": random.choice([3500, 8000, 15000, 25000]),
                        "premium_frequency": random.choice(frequencies),
                        "start_date": start,
                        "expiry_date": expiry,
                        "status": random.choice(statuses),
                        "notes": "",
                    },
                )
                policies.append(policy)

        # --- Payments (a couple per policy) ---
        for policy in policies:
            for i in range(random.randint(1, 3)):
                Payment.objects.get_or_create(
                    policy=policy,
                    date_paid=policy.start_date + datetime.timedelta(days=30 * i),
                    defaults={
                        "amount_paid": policy.premium_amount,
                        "payment_method": random.choice(Payment.Method.values),
                        "reference_number": f"TXN{random.randint(100000, 999999)}",
                        "period_covered": f"Period {i + 1}",
                    },
                )

        # --- Premium schedule (next 2 due dates per active policy) ---
        for policy in policies:
            if policy.status == Policy.Status.ACTIVE:
                for i in range(1, 3):
                    PremiumSchedule.objects.get_or_create(
                        policy=policy,
                        due_date=today + datetime.timedelta(days=30 * i),
                        defaults={
                            "amount_due": policy.premium_amount,
                            "status": PremiumSchedule.Status.PENDING,
                        },
                    )

        # --- Beneficiaries (life policies only) ---
        for policy in policies:
            if policy.policy_type.name == "Life":
                Beneficiary.objects.get_or_create(
                    policy=policy,
                    full_name=f"{policy.customer.full_name.split()[0]}'s Spouse",
                    defaults={
                        "relationship_to_policyholder": "Spouse",
                        "percentage_share": 100,
                        "contact_info": policy.customer.phone_number,
                    },
                )

        # --- A couple of claims with status history ---
        claimable_policies = random.sample(policies, k=min(3, len(policies)))
        for policy in claimable_policies:
            claim, created = Claim.objects.get_or_create(
                policy=policy,
                date_filed=today - datetime.timedelta(days=random.randint(5, 60)),
                defaults={
                    "description": f"Claim on {policy.policy_type.name} policy {policy.policy_number}",
                    "amount_claimed": random.choice([20000, 50000, 120000]),
                    "current_status": Claim.Status.UNDER_REVIEW,
                },
            )
            if created:
                ClaimStatusHistory.objects.create(
                    claim=claim, status=Claim.Status.FILED, note="Claim received."
                )
                ClaimStatusHistory.objects.create(
                    claim=claim, status=Claim.Status.UNDER_REVIEW, note="Assessor assigned."
                )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(customers)} customers, {len(policies)} policies, "
            f"{Payment.objects.count()} payments, {Claim.objects.count()} claims."
        ))
