from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import date
from django.utils import timezone
import calendar

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    class Meta:
        abstract = True
        
        
class Module(BaseModel):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Role(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    modules = models.ManyToManyField(Module, through='RoleModuleAccess')
    h_name = models.CharField(max_length=100, blank=True, null=True)
    sn = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

class RoleModuleAccess(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        extra_fields.setdefault('is_active', True)
        user.save(using=self._db)
        return user
    def create_superuser(self, username, password=None, **extra_fields):
        # Auto-assign default role 'Admin' if not given
        if 'role' not in extra_fields or extra_fields['role'] is None:
            try:
                admin_role, created = Role.objects.get_or_create(name='Admin')
            except Role.DoesNotExist:
                raise ValueError("❌ Role 'Admin' does not exist. Please create it first.")
            extra_fields['role'] = admin_role
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150,default='Anonymous')
    mobile_no = models.CharField(max_length=50,null=True,blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Roles
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    picture = models.ImageField(upload_to='users/',null=True, blank=True)

    objects = CustomUserManager()
    
 

    USERNAME_FIELD = 'username'
    def __str__(self):
        return f"{self.username} - {self.role.name if self.role else 'No Role'}"




class Location(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class School(BaseModel):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Subject(BaseModel):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class StudentClass(BaseModel):
    number = models.IntegerField(unique=True)
    active = models.BooleanField(default=True)
    inactive_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.number)

class Teacher(BaseModel):
    BLOOD_LIST = [
        ("a+", "A+"),
        ("a-", "A-"),
        ("b+", "B+"),
        ("b-", "B-"),
        ("o+", "O+"),
        ("o-", "O-"),
        ("ab+", "AB+"),
        ("ab-", "AB-"),
    ]
    GENDER_LIST = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    MARITAL_STATUS_LIST = [
        ("single", "Single"),
        ("married", "Married"),
        ("unmarried", "Unmarried"),
        ("divorced", "Divorced"),
        ("widowed", "Widowed"),
        ("separated", "Separated"),
    ]
    RELIGION_LIST = [
        ("hindu", "Hindu"),
        ("muslim", "Muslim"),
        ("christian", "Christian"),
        ("sikh", "Sikh"),
        ("jain", "Jain"),
        ("buddhist", "Buddhist"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    mob_no = models.CharField(max_length=50, null=True, blank=True)
    picture = models.ImageField(upload_to='teachers/', null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, choices=GENDER_LIST, null=True, blank=True)
    marital_status = models.CharField(max_length=150,choices=MARITAL_STATUS_LIST, null=True, blank=True)
    blood = models.CharField(max_length=50, choices=BLOOD_LIST, null=True, blank=True)
    religion = models.CharField(max_length=50, choices=RELIGION_LIST, null=True, blank=True)
    active = models.BooleanField(default=True)
    inactive_date = models.DateField(null=True, blank=True)
    @property
    def age(self):
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    def __str__(self):
        return self.name
    def __str__(self):
        return self.name if self.name else "Unnamed Teacher"

class Student(BaseModel):
    BLOOD_LIST = [
        ("a+", "A+"),
        ("a-", "A-"),
        ("b+", "B+"),
        ("b-", "B-"),
        ("o+", "O+"),
        ("o-", "O-"),
        ("ab+", "AB+"),
        ("ab-", "AB-"),
    ]
    GENDER_LIST = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    MARITAL_STATUS_LIST = [
        ("single", "Single"),
        ("married", "Married"),
        ("unmarried", "Unmarried"),
        ("divorced", "Divorced"),
        ("widowed", "Widowed"),
        ("separated", "Separated"),
    ]
    RELIGION_LIST = [
        ("hindu", "Hindu"),
        ("muslim", "Muslim"),
        ("christian", "Christian"),
        ("sikh", "Sikh"),
        ("jain", "Jain"),
        ("buddhist", "Buddhist"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student', blank=True, null=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    mob_no = models.CharField(max_length=50, null=True, blank=True)
    picture = models.ImageField(upload_to='students/', null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    roll_no = models.CharField(max_length=50, unique=True)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    mother_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    father_mob_no = models.CharField(max_length=50, null=True, blank=True)
    mother_mob_no = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=50, choices=GENDER_LIST, null=True, blank=True)
    marital_status = models.CharField(max_length=150,choices=MARITAL_STATUS_LIST, null=True, blank=True)
    blood = models.CharField(max_length=50, choices=BLOOD_LIST, null=True, blank=True)
    religion = models.CharField(max_length=50, choices=RELIGION_LIST, null=True, blank=True)
    active = models.BooleanField(default=True)
    inactive_date = models.DateField(null=True, blank=True)
    join_date = models.DateField(auto_now_add=True, null=True, blank=True)
    @property
    def age(self):
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    def __str__(self):
        return self.name
    
    
class TeachingAssignment(BaseModel):
    date = models.DateField(null=True,blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.student_class}"

class ExamResult(BaseModel):
    date = models.DateField(default=timezone.now)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_mark = models.IntegerField(null=True, blank=True)
    obtained_mark = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher} - {self.student} - {self.subject}"
    
class Message(BaseModel):
    text = models.TextField(null=True,blank=True)
    student_class = models.ForeignKey(StudentClass,on_delete=models.CASCADE)
    total_sms_count = models.IntegerField(default=0)
    
    
class MonthlyPayment(models.Model):
    code = models.IntegerField(null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='monthly_payments')
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)  # 1 = January, 12 = December
    amount = models.IntegerField(null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True,null=True,blank=True)

    class Meta:
        unique_together = ('student', 'year', 'month')  # prevent duplicate payments

    def __str__(self):
        return f"{self.student.name} - {calendar.month_name[self.month]} {self.year}"
    
    
# models.py
class SMSCounter(models.Model):
    total_sms_sent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"SMS Sent: {self.total_sms_sent} (Started {self.created_at})"




class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    is_present = models.BooleanField()

    class Meta:
        unique_together = ('student', 'date')  # Prevent duplicate entries