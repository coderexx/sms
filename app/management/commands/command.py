# management/commands/seed_modules.py
from django.core.management.base import BaseCommand
from app.models import *
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

class Command(BaseCommand):
    help = "Delete duplicate locations based on name"

    def handle(self, *args, **kwargs):
        duplicates = (
            Location.objects
            .values("name")
            .annotate(name_count=Count("id"))
            .filter(name_count__gt=1)
        )

        total_deleted = 0

        for dup in duplicates:
            # Get all objects with this duplicate name
            locations = Location.objects.filter(name=dup["name"]).order_by("id")
            
            # Keep the first, delete the rest
            to_delete = locations[1:]
            deleted_count, _ = to_delete.delete()
            total_deleted += deleted_count

        self.stdout.write(self.style.SUCCESS(f"✅ Done! {total_deleted} duplicate locations deleted."))
