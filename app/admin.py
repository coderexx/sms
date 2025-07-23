from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location')
    search_fields = ('name',)
    list_filter = ('location',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass
    
@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'number')
    
@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    pass