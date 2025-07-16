from django.core.management.base import BaseCommand
from account.models import District, Upazila  # adjust app name
from django.db import transaction
from account.address import *


class Command(BaseCommand):
    help = "Insert all districts and upazilas of Bangladesh"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Step 1: Create Districts
            district_objs = [District(name=name) for name in district_upazila_data.keys()]
            District.objects.bulk_create(district_objs, ignore_conflicts=True)

            # Step 2: Fetch all districts as a name:object dictionary
            districts = {d.name: d for d in District.objects.filter(name__in=district_upazila_data.keys())}

            # Step 3: Create Upazilas
            upazilas = []
            for district_name, upazila_names in district_upazila_data.items():
                district = districts[district_name]
                for upazila_name in upazila_names:
                    upazilas.append(Upazila(name=upazila_name, district=district))

            Upazila.objects.bulk_create(upazilas, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("✅ Districts and Upazilas inserted successfully."))

