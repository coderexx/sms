from django.contrib import admin
from .models import *
from .forms import RoleAdminForm 

# Register your models here.

class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ['name']
    # inlines = [RoleModuleAccessInline]
    class Media:
        css = {
            'all': ('admin/css/custom_module_checkbox.css',)
        }
    

class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
admin.site.register(Module, ModuleAdmin)
admin.site.register(Role, RoleAdmin)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'mobile_no', 'role']
    search_fields = ['username', 'name', 'mobile_no']
    list_filter = ['role']
admin.site.register(CustomUser, CustomUserAdmin)




@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location')
    search_fields = ('name',)
    list_filter = ('location',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass

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

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    pass 

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    pass


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass

@admin.register(SMSCounter)
class SMSCounterAdmin(admin.ModelAdmin):
    pass