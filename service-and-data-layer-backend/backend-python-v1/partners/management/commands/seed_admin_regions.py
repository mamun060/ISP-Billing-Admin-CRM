from django.core.management.base import BaseCommand

from partners.models import Division, District, Upazila, Union


SAMPLE = [
    {
        "name": "Dhaka",
        "code": "DHA",
        "districts": [
            {"name": "Dhaka District", "code": "DHA-D"},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed a minimal set of administrative regions (Division/District/Upazila/Union)"

    def handle(self, *args, **options):
        for d in SAMPLE:
            div, _ = Division.objects.get_or_create(name=d["name"], code=d.get("code"))
            for dist in d.get("districts", []):
                district, _ = District.objects.get_or_create(name=dist["name"], division=div, code=dist.get("code"))
        self.stdout.write(self.style.SUCCESS("Seeded admin regions"))
