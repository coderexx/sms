from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from account.models import Member
from django.db import DatabaseError

User = get_user_model()

class Command(BaseCommand):
    help = "Clears default pictures in both User and Member models"

    def handle(self, *args, **options):
        default_path = "members/default.png"
        user_updated = 0
        member_updated = 0
        user_skipped = 0
        member_skipped = 0

        # Process Users
        for user in User.objects.all():
            if hasattr(user, 'picture') and user.picture and str(user.picture) == default_path:
                user.picture = None
                try:
                    user.save()
                    user_updated += 1
                except DatabaseError as e:
                    self.stdout.write(self.style.WARNING(f"Skipped user {user.pk} due to DB error: {e}"))
                    user_skipped += 1

        # Process Members
        for member in Member.objects.all():
            if hasattr(member, 'picture') and member.picture and str(member.picture) == default_path:
                member.picture = None
                try:
                    member.save()
                    member_updated += 1
                except DatabaseError as e:
                    self.stdout.write(self.style.WARNING(f"Skipped member {member.pk} due to DB error: {e}"))
                    member_skipped += 1

        self.stdout.write(self.style.SUCCESS(f"{user_updated} User(s) updated, {user_skipped} skipped."))
        self.stdout.write(self.style.SUCCESS(f"{member_updated} Member(s) updated, {member_skipped} skipped."))
