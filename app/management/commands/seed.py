# management/commands/seed_modules.py
from django.core.management.base import BaseCommand
from app.models import Module

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        module_names = [
            # Student
            'create_student', 'read_student', 'update_student', 'delete_student',
            # Teacher
            'create_teacher', 'read_teacher', 'update_teacher', 'delete_teacher',
            # User
            'create_user', 'read_user', 'update_user', 'delete_user',
            # Student Class
            'create_student_class', 'read_student_class', 'update_student_class', 'delete_student_class',
            # Location
            'create_location', 'read_location', 'update_location', 'delete_location',
            # School
            'create_school', 'read_school', 'update_school', 'delete_school',
            # Subject
            'create_subject', 'read_subject', 'update_subject', 'delete_subject',
            # Teaching Assignment
            'create_teaching_assignment', 'read_teaching_assignment', 'delete_teaching_assignment',
            # Message
            'create_message', 'read_message', 'reset_sms_counter',
            # Payment
            'due_table', 'make_payment', 'read_credit',
            # Attendance
            'take_attendance', 'attendance_report',
            # Settings
            'database', 'change_password',
        ]
        Module.objects.exclude(name__in=module_names).delete()
        for name in module_names:
            Module.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Modules created."))
