# management/commands/seed_modules.py
from django.core.management.base import BaseCommand
from app.models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        students = Student.object.all()
        role = Role.objects.get(h_name="student")
        count = 0
        for i in students:
            user = User.object.create(role=role, username=i.role_no, password=i.mob_no, name=i.name, mobile_no=i.mob_no, picture=i.picture)
            i.user = user
            i.save()
            count=count+1


        self.stdout.write(self.style.SUCCESS(f"🎉 Done ! {count} have been updated"))