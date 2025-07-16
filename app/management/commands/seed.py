# management/commands/seed_modules.py
from django.core.management.base import BaseCommand
from app.models import Module

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        module_names = [
            'create_student','read_student','update_student','delete_student',
            'create_teacher','read_teacher','update_teacher','delete_teacher',
            'create_class','read_class','update_class','delete_class',
            'create_location','read_location','update_location','delete_location',
            'create_school','read_school','update_school','delete_school',
        ]
        Module.objects.exclude(name__in=module_names).delete()
        for name in module_names:
            Module.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Modules created."))
