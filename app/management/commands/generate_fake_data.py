from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import date
from app.models import Location, School, StudentClass, Teacher, Student

class Command(BaseCommand):
    help = 'Generate fake data for Location, School, StudentClass, Teacher, and Student'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Locations
        locations = []
        for _ in range(10):
            loc = Location.objects.create(name=fake.city())
            locations.append(loc)
        self.stdout.write(self.style.SUCCESS("✅ Created 10 Locations"))

        # Create Student Classes
        classes = []
        for i in range(1, 10):
            c = StudentClass.objects.create(number=i, active=True)
            classes.append(c)
        self.stdout.write(self.style.SUCCESS("✅ Created 10 Student Classes"))

        # Create Schools
        schools = []
        for _ in range(5):
            sch = School.objects.create(name=fake.company(), location=random.choice(locations))
            schools.append(sch)
        self.stdout.write(self.style.SUCCESS("✅ Created 5 Schools"))

        # Choices
        GENDER_LIST = ["male", "female"]
        MARITAL_STATUS_LIST = ["single", "married", "unmarried", "divorced", "widowed", "separated"]
        BLOOD_LIST = ["a+", "a-", "b+", "b-", "o+", "o-", "ab+", "ab-"]
        RELIGION_LIST = ["hindu", "muslim", "christian", "sikh", "jain", "buddhist", "other"]

        # Create Teachers
        for _ in range(50):
            Teacher.objects.create(
                name=fake.name(),
                location=random.choice(locations),
                mob_no=fake.phone_number(),
                email=fake.email(),
                date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=60),
                gender=random.choice(GENDER_LIST),
                marital_status=random.choice(MARITAL_STATUS_LIST),
                blood=random.choice(BLOOD_LIST),
                religion=random.choice(RELIGION_LIST),
                active=True,
            )
        self.stdout.write(self.style.SUCCESS("✅ Created 50 Teachers"))

        # Create Students
        for _ in range(2000):
            Student.objects.create(
                name=fake.name(),
                school=random.choice(schools),
                student_class=random.choice(classes),
                location=random.choice(locations),
                mob_no=fake.phone_number(),
                email=fake.email(),
                roll_no=str(fake.random_int(min=1000, max=9999)),
                father_name=fake.name_male(),
                mother_name=fake.name_female(),
                date_of_birth=fake.date_of_birth(minimum_age=6, maximum_age=18),
                father_mob_no=fake.phone_number(),
                mother_mob_no=fake.phone_number(),
                gender=random.choice(GENDER_LIST),
                marital_status=random.choice(MARITAL_STATUS_LIST),
                blood=random.choice(BLOOD_LIST),
                religion=random.choice(RELIGION_LIST),
                active=True,
            )
        self.stdout.write(self.style.SUCCESS("✅ Created 2000 Students"))
        self.stdout.write(self.style.SUCCESS("🎉 Done generating fake data!"))
