# management/commands/seed_modules.py
from django.core.management.base import BaseCommand
from app.models import Student, Role
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        students = Student.objects.all()
        role, created = Role.objects.get_or_create(h_name="student")
        count = 0

        for i in students:
            if not i.user:  # only if student is not already linked to a user
                user = User.objects.create_user(
                    username=i.roll_no,         # Student roll no as username
                    password=i.mob_no,          # Mobile no as password (hashed)
                    name=i.name,
                    mobile_no=i.mob_no,
                    role=role,
                    picture=i.picture
                )
                i.user = user
                i.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(f"🎉 Done! {count} students have been linked to users"))
