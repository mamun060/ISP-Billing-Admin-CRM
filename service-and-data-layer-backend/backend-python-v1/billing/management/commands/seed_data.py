from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

import random


class Command(BaseCommand):
    help = "Seed divisions, districts, upazilas and create test clients."

    def add_arguments(self, parser):
        parser.add_argument("--clients", type=int, default=500, help="Number of clients to create")
        parser.add_argument("--password", type=str, default="password123", help="Password for created user accounts")
        parser.add_argument("--divisions", type=int, default=8, help="Number of divisions to create")
        parser.add_argument("--districts-per-division", type=int, default=5)
        parser.add_argument("--upazilas-per-district", type=int, default=3)

    def handle(self, *args, **options):
        clients_count = options["clients"]
        password = options["password"]
        divisions_count = options["divisions"]
        districts_per_div = options["districts_per_division"]
        upazilas_per_dist = options["upazilas_per_district"]

        from partners.models import Division, District, Upazila
        from billing.models import Client
        from packages.models import Package
        from partners.models import Partner
        from accounts.models import User

        self.stdout.write("Seeding location data...")

        divisions = []
        districts = []
        upazilas = []

        with transaction.atomic():
            for d in range(1, divisions_count + 1):
                name = f"Division {d}"
                div, _ = Division.objects.get_or_create(name=name, defaults={"code": f"DIV{d}"})
                divisions.append(div)
                for di in range(1, districts_per_div + 1):
                    dname = f"District {d}.{di}"
                    dist, _ = District.objects.get_or_create(name=dname, defaults={"division": div, "code": f"DIS{d}{di}"})
                    districts.append(dist)
                    for u in range(1, upazilas_per_dist + 1):
                        uname = f"Upazila {d}.{di}.{u}"
                        up, _ = Upazila.objects.get_or_create(name=uname, defaults={"district": dist, "code": f"UPA{d}{di}{u}"})
                        upazilas.append(up)

        self.stdout.write(self.style.SUCCESS(f"Created/ensured {len(divisions)} divisions, {len(districts)} districts, {len(upazilas)} upazilas"))

        # Ensure at least one Package and Partner exist
        package = Package.objects.first()
        if not package:
            package = Package.objects.create(name="Default Package", type="internet", price=500.00, validity_days=30, status="active")
            self.stdout.write(self.style.SUCCESS("Created default Package"))

        partner = Partner.objects.first()
        if not partner:
            partner = Partner.objects.create(name="Default Partner", code="PART-DEFAULT", type="ZONE")
            self.stdout.write(self.style.SUCCESS("Created default Partner"))

        self.stdout.write("Seeding clients...")

        clients = []
        phones = set()
        for i in range(1, clients_count + 1):
            phone = f"0199{str(10000000 + i)}"[-11:]
            # ensure uniqueness
            while phone in phones:
                i += 1
                phone = f"0199{str(10000000 + i)}"[-11:]
            phones.add(phone)

            name = f"Test Client {i}"
            div = random.choice(divisions)
            # pick a district and upazila under chosen division if possible
            dists = list(div.districts.all())
            if dists:
                dist = random.choice(dists)
                upas = list(dist.upazilas.all())
                upa = random.choice(upas) if upas else None
            else:
                dist = random.choice(districts) if districts else None
                upa = random.choice(upazilas) if upazilas else None

            client = Client(name=name, phone=phone, client_type="residential", owning_partner=partner, package=package, status="active", division=div, district=dist, upazila=upa)
            clients.append(client)

        Client.objects.bulk_create(clients)
        self.stdout.write(self.style.SUCCESS(f"Created {len(clients)} clients"))

        # Create corresponding User accounts with same password if not exist
        created_users = 0
        for client in clients:
            try:
                # phone is login identifier for User
                if not User.objects.filter(phone=client.phone).exists():
                    User.objects.create_user(phone=client.phone, password=password, username=client.phone, email=f"{slugify(client.name)}+{client.phone}@example.com")
                    created_users += 1
            except Exception:
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created_users} user accounts for clients (password='{password}')"))

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
