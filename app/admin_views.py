from datetime import datetime, date
import os
import subprocess
from io import BytesIO
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.db import transaction

from app.views import User
from .utils.decorators import role_required
from .utils.send_sms import send_sms
from .models import *
#for pdf
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required


# global variables
today = date.today()

@login_required
def dashboard(request):
    total_active_students = Student.objects.filter(active=True, student_class__active=True).count()
    total_active_teachers = Teacher.objects.filter(active=True).count()

    active_classes = StudentClass.objects.filter(active=True).order_by('number')
    class_data = []

    for cls in active_classes:
        student_count = Student.objects.filter(student_class=cls, active=True).count()
        male_count = Student.objects.filter(student_class=cls, active=True, gender='male').count()
        female_count = Student.objects.filter(student_class=cls, active=True, gender='female').count()
        class_data.append({
            'class': cls,
            'student_count': student_count,
            'male_count': male_count,
            'female_count': female_count
        })

    context = {
        'total_active_students': total_active_students,
        'total_active_teachers': total_active_teachers,
        'class_data': class_data
    }

    return render(request, 'admin/dashboard.html', context)



#TODO:Student
#read_student
@login_required
def read_student(request):
    students = Student.objects.filter(active=True,student_class__active=True).order_by('name')
    
    
    #get query parameters
    query = request.GET.get('query', '')
    student_class_query = request.GET.get('student_class_query', '')
    school_query = request.GET.get('school_query', '')
    location_query = request.GET.get('location_query', '')
    blood_query = request.GET.get('blood_query', '')
    religion_query = request.GET.get('religion_query', '')
    gender_query = request.GET.get('gender_query', '')
    marital_status_query = request.GET.get('marital_status_query', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query) |
            Q(roll_no__icontains=query)
        )
    if student_class_query:
        students = students.filter(student_class__id=student_class_query)
    if school_query:
        students = students.filter(school__id=school_query)
    if location_query:
        students = students.filter(location__id=location_query)
    if blood_query:
        students = students.filter(blood=blood_query)
    if religion_query:
        students = students.filter(religion=religion_query)
    if gender_query:
        students = students.filter(gender=gender_query)
    if marital_status_query:
        students = students.filter(marital_status=marital_status_query)
        
        
    # pagination for main_leave
    paginator = Paginator(students, 50)  # 50 records per page
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "students": students,
        "query_string": query_string,
        "student_classes": StudentClass.objects.filter(active=True).order_by('number'),
        "schools": School.objects.all().order_by('name'),
        "locations": Location.objects.all().order_by('name'),
        "bloods": Student.BLOOD_LIST,
        "religions": Student.RELIGION_LIST,
        "genders": Student.GENDER_LIST,
        "marital_statuses": Student.MARITAL_STATUS_LIST,
        "query": query,
        "student_class_query": int(student_class_query) if student_class_query else None,
        "school_query": int(school_query) if school_query else None,
        "location_query": int(location_query) if location_query else None,
        "blood_query": blood_query,
        "religion_query": religion_query,
        "gender_query": gender_query,
        "marital_status_query": marital_status_query
    }
    return render(request,'student/read_student.html',context)

@login_required
def read_inactive_student(request):
    students = Student.objects.filter(
        Q(active=False) | Q(student_class__active=False)
    ).order_by('name')
    
        # pagination for main_leave
    paginator = Paginator(students, 50)  # 50 records per page
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "students": students,
        "query_string": query_string,
        "inactive": True
    }
    return render(request,'student/read_student.html',context)

#create_student
@login_required
def create_student(request):
    if request.method == 'POST':
        # ✅ Extract Required Fields
        name = request.POST.get('name')
        school_id = request.POST.get('school')
        student_class_id = request.POST.get('student_class')
        mob_no = request.POST.get('mob_no')
        gender = request.POST.get('gender')
        location_id = request.POST.get('location') or None
        email = request.POST.get('email')
        roll_no = request.POST.get('roll_no')
        father_name = request.POST.get('father_name')
        mother_name = request.POST.get('mother_name')
        date_of_birth = request.POST.get('date_of_birth') or None
        father_mob_no = request.POST.get('father_mob_no')
        mother_mob_no = request.POST.get('mother_mob_no')
        marital_status = request.POST.get('marital_status')
        blood = request.POST.get('blood')
        religion = request.POST.get('religion')
        
        # ✅ Manual Required Validation
        if not all([name, school_id, student_class_id, mob_no]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('create_student')

        # ✅ Create Student Object
        student = Student(name=name, school_id=school_id, student_class_id=student_class_id, location_id=location_id, mob_no=mob_no, email=email, roll_no=roll_no, father_name=father_name, mother_name=mother_name, date_of_birth=date_of_birth, father_mob_no=father_mob_no, mother_mob_no=mother_mob_no, gender=gender, marital_status=marital_status, blood=blood, religion=religion, active=True)

        # ✅ Handle Picture Upload
        if request.FILES.get('picture'):
            student.picture = request.FILES['picture']

        student.save()
        messages.success(request, 'Student added successfully.')
        return redirect('create_student')
    
    context = {
        'schools': School.objects.all().order_by('name'),
        'locations': Location.objects.all().order_by('name'),
        'student_classes': StudentClass.objects.filter(active=True).order_by('number'),
        'genders': Student.GENDER_LIST,
        'bloods': Student.BLOOD_LIST,
        'religions': Student.RELIGION_LIST,
        'marital_statuses': Student.MARITAL_STATUS_LIST
    }
    return render(request,'student/create_student.html',context)

#update_student
@login_required
def update_student(request,id):
    student = get_object_or_404(Student, id=id)
    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.school_id = request.POST.get('school')
        student.student_class_id = request.POST.get('student_class')
        student.location_id = request.POST.get('location') or None
        student.mob_no = request.POST.get('mob_no')
        student.email = request.POST.get('email')
        student.roll_no = request.POST.get('roll_no')
        student.father_name = request.POST.get('father_name')
        student.mother_name = request.POST.get('mother_name')
        student.date_of_birth = request.POST.get('date_of_birth') or None
        student.father_mob_no = request.POST.get('father_mob_no')
        student.mother_mob_no = request.POST.get('mother_mob_no')
        student.gender = request.POST.get('gender')
        student.marital_status = request.POST.get('marital_status')
        student.blood = request.POST.get('blood')
        student.religion = request.POST.get('religion')
        if request.FILES.get('picture'):
            student.picture = request.FILES['picture']
        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('read_student')

    context = {
        'student': student,
        'schools': School.objects.all().order_by('name'),
        'locations': Location.objects.all().order_by('name'),
        'student_classes': StudentClass.objects.filter(active=True).order_by('number'),
        'genders': Student.GENDER_LIST,
        'bloods': Student.BLOOD_LIST,
        'religions': Student.RELIGION_LIST,
        'marital_statuses': Student.MARITAL_STATUS_LIST
    }
    return render(request,'student/update_student.html',context)

#delete_student
@login_required
def delete_student(request,id):
    student = Student.objects.get(id=id)
    messages.success(request,f"{student.name} was deleted successfully.")
    return redirect(read_student)

#activation_student
@login_required
def activation_student(request,id):
    student = Student.objects.get(id=id)
    if student.active == True:
        student.active = False
        messages.success(request,f"{student.name} was deactivation successfully.")
    else:
        student.active = True
        messages.success(request,f"{student.name} was activation successfully.")
    student.save()
    return redirect(read_student)




#TODO:Teacher
#read_teacher
@login_required
def read_teacher(request):
    teachers = Teacher.objects.filter(active=True).order_by('name')
    
    
    query = request.GET.get('query', '')
    if query:
        teachers = teachers.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query)
        )
    
    
    # pagination for main_leave
    paginator = Paginator(teachers, 50)  # 50 records per page
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "teachers":teachers,
        "query_string": query_string,
        "query": query,
    }
    return render(request,'teacher/read_teacher.html',context)

@login_required
def read_inactive_teacher(request):
    teachers = Teacher.objects.filter(active=False).order_by('name')
    
    # pagination for main_leave
    paginator = Paginator(teachers, 50)  # 50 records per page
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "teachers":teachers,
        "inactive": True
    }
    return render(request,'teacher/read_teacher.html',context)

#create_teacher
@login_required
def create_teacher(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mob_no = request.POST.get('mob_no')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth') or None
        marital_status = request.POST.get('marital_status')
        blood = request.POST.get('blood')
        religion = request.POST.get('religion')
        location_id = request.POST.get('location') or None

        if not all([name, mob_no]):
            messages.error(request, "Name, Mobile No, and Gender are required.")
            return redirect('create_teacher')

        teacher = Teacher.objects.create(name=os.name, mob_no=mob_no, gender=gender, email=email, date_of_birth=date_of_birth, marital_status=marital_status, blood=blood, religion=religion, location_id=location_id, active=True)


        if request.FILES.get('picture'):
            teacher.picture = request.FILES['picture']

        teacher.save()
        messages.success(request, "Teacher created successfully.")
        return redirect('create_teacher')

    context = {
        'genders': Teacher.GENDER_LIST,
        'bloods': Teacher.BLOOD_LIST,
        'religions': Teacher.RELIGION_LIST,
        'marital_statuses': Teacher.MARITAL_STATUS_LIST,
        'locations': Location.objects.all()
    }
    return render(request,'teacher/create_teacher.html',context)

#update_teacher
@login_required
def update_teacher(request,id):
    teacher = get_object_or_404(Teacher, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        mob_no = request.POST.get('mob_no')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth') or None
        marital_status = request.POST.get('marital_status')
        blood = request.POST.get('blood')
        religion = request.POST.get('religion')
        location_id = request.POST.get('location') or None

        # Optional: Validate required fields
        if not all([name, mob_no]):
            messages.error(request, "Name, Mobile No are required.")
            return redirect('update_teacher', id=id)

        # Update fields
        teacher.name = name
        teacher.mob_no = mob_no
        teacher.gender = gender
        teacher.email = email
        teacher.date_of_birth = date_of_birth
        teacher.marital_status = marital_status
        teacher.blood = blood
        teacher.religion = religion
        teacher.location_id = location_id

        if request.FILES.get('picture'):
            teacher.picture = request.FILES['picture']

        teacher.save()
        messages.success(request, "Teacher updated successfully.")
        return redirect('read_teacher')

    # GET request — show the form with existing data
    context = {
        'teacher': teacher,
        'locations': Location.objects.all(),
        'genders': Teacher.GENDER_LIST,
        'bloods': Teacher.BLOOD_LIST,
        'religions': Teacher.RELIGION_LIST,
        'marital_statuses': Teacher.MARITAL_STATUS_LIST,
    }
    return render(request,'teacher/update_teacher.html',context)

#delete_teacher
@login_required
def delete_teacher(request,id):
    teacher = Teacher.objects.get(id=id)
    messages.success(request,f"{teacher.name} was deleted successfully.")
    return redirect(read_teacher)

#activation_teacher
@login_required
def activation_teacher(request,id):
    teacher = Teacher.objects.get(id=id)
    if teacher.active == True:
        teacher.active = False
        messages.success(request,f"{teacher.name} was deactivation successfully.")
    else:
        teacher.active = True
        messages.success(request,f"{teacher.name} was activation successfully.")
    teacher.save()
    return redirect(read_teacher)







#TODO:StudentClass
#read_student_class
@login_required
def read_student_class(request):
    student_classes = StudentClass.objects.all().order_by('number')
    
    # pagination for main_leave
    paginator = Paginator(student_classes, 50)  # 50 records per page
    page_number = request.GET.get('page')
    student_classes = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "student_classes":student_classes,
        "query_string": query_string
    }
    return render(request,'student_class/read_student_class.html',context)

#create_student_class
@login_required
def create_student_class(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        
        student_class = StudentClass(
            number=number,
        )
        student_class.save()
        messages.success(request, f"Class {number} was created successfully.")
        return redirect(read_student_class)
    context = {
        
    }
    return render(request,'student_class/create_student_class.html',context)

#update_student_class
@login_required
def update_student_class(request,id):
    student_class = get_object_or_404(StudentClass, id=id)
    if request.method == 'POST':
        number = request.POST.get('number')
        student_class.number = number
        student_class.save()
        messages.success(request, f"Class {number} was updated successfully.")
        return redirect(read_student_class)
    context = {
        "student_class": student_class
    }
    return render(request,'student_class/update_student_class.html',context)

#delete_student_class
@login_required
def delete_student_class(request,id):
    student_class = StudentClass.objects.get(id=id)
    messages.success(request,f"{student_class.number} was deleted successfully.")
    return redirect(read_student_class)


#activation_student_class
@login_required
def activation_student_class(request,id):
    student_class = StudentClass.objects.get(id=id)
    if student_class.active == True:
        student_class.active = False
        messages.success(request,f"class {student_class.number} was deactivation successfully.")
    else:
        student_class.active = True
        messages.success(request,f"class {student_class.number} was activation successfully.")
    student_class.save()
    return redirect(read_student_class)

#shift_down_student_class
@login_required
def shift_down_student_class(request):
    student_classes = StudentClass.objects.all().order_by('number')  # Important: reverse order!

    if student_classes.exists():
        try:
            with transaction.atomic():
                for student_class in student_classes:
                    student_class.number -= 1
                    student_class.save()
            messages.success(request, "All active classes have been shifted down by one.")
        except Exception as e:
            messages.error(request, f"Error occurred: {str(e)}")
    else:
        messages.error(request, "No active classes found to shift down.")

    return redirect(read_student_class)

#student_class_shift_up
@login_required
def shift_up_student_class(request):
    student_classes = StudentClass.objects.all().order_by('-number')  # Important: reverse order!

    if student_classes.exists():
        try:
            with transaction.atomic():
                for student_class in student_classes:
                    student_class.number += 1
                    student_class.save()
            messages.success(request, "All active classes have been shifted up by one.")
        except Exception as e:
            messages.error(request, f"Error occurred: {str(e)}")
    else:
        messages.error(request, "No active classes found to shift up.")

    return redirect(read_student_class)

#student profile
@login_required
def profile_student(request,id):
    student = Student.objects.get(id=id)
    context = {
        "student":student
    }
    return render(request,'profile/student_profile.html',context)

#teacher profile
@login_required
def profile_teacher(request,id):
    teacher = Teacher.objects.get(id=id)
    context = {
        "teacher":teacher
    }
    return render(request,'profile/teacher_profile.html',context)
    
    
    
@login_required
def to_int_or_none(val):
    if not val or val.strip().lower() == 'none':
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
@login_required
def read_student_pdf(request):
    students = Student.objects.filter(active=True,student_class__active=True).order_by('name')
    
    #get query parameters
    query = request.GET.get('query', '')
    student_class_query = to_int_or_none(request.GET.get('student_class_query'))
    school_query = to_int_or_none(request.GET.get('school_query'))
    location_query = to_int_or_none(request.GET.get('location_query'))
    blood_query = request.GET.get('blood_query', '')
    religion_query = request.GET.get('religion_query', '')
    gender_query = request.GET.get('gender_query', '')
    marital_status_query = request.GET.get('marital_status_query', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query) |
            Q(roll_no__icontains=query)
        )
    if student_class_query is not None:
        students = students.filter(student_class__id=student_class_query)
    if school_query is not None:
        students = students.filter(school__id=school_query)
    if location_query is not None:
        students = students.filter(location__id=location_query)
    if blood_query:
        students = students.filter(blood=blood_query)
    if religion_query:
        students = students.filter(religion=religion_query)
    if gender_query:
        students = students.filter(gender=gender_query)
    if marital_status_query:
        students = students.filter(marital_status=marital_status_query)
        
    context = {
        "students": students
    }
    # Load the HTML template and render it with context data
    template = get_template('pdf/read_student_pdf.html')
    html = template.render(context)

    # Create a response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="students.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    return response



@login_required
def read_teacher_pdf(request):
    teachers = Teacher.objects.filter(active=True).order_by('name')
    
    #get query parameters
    query = request.GET.get('query', '')
    if query:
        teachers = teachers.filter(
            Q(name__icontains=query) |
            Q(mob_no__icontains=query) |
            Q(email__icontains=query)
        )
        
    context = {
        "teachers": teachers
    }
    # Load the HTML template and render it with context data
    template = get_template('pdf/read_teacher_pdf.html')
    html = template.render(context)

    # Create a response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="teachers.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    return response


#TODO:Message
@login_required
def read_message(request):
    messages = Message.objects.all().order_by('-created_at')
    
    #get query parameters
    student_class_query = request.GET.get('student_class_query', '')
    if student_class_query:
        messages = messages.filter(student_class__id=student_class_query)
        
    # pagination for main_leave
    paginator = Paginator(messages, 50)  # 50 records per page
    page_number = request.GET.get('page')
    messages = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "messages": messages,
        "student_classes": StudentClass.objects.filter(active=True).order_by('number'),
        "student_class_query": int(student_class_query) if student_class_query else None,
        "query_string": query_string
    }
    return render(request,'messages/read_message.html',context)


@login_required
def create_message(request):
    if request.method == 'POST':
        student_class = request.POST.get('student_class')
        text = request.POST.get('text')
        # Send SMS to all students in the selected class
        students = Student.objects.filter(student_class_id=student_class, active=True)
        for student in students:
            if student.mob_no:
                success, response = send_sms(student.mob_no, student.name, text)
                if not success:
                    messages.error(request, f"Failed to send SMS to {student.name}: {response}")
                    
        message = Message(
            student_class_id=student_class,
            text=text,
        )
        message.save()
        messages.success(request, f"Message was created successfully.")
        return redirect(read_message)
    context = { 
        "student_classes": StudentClass.objects.filter(active=True).order_by('number'),
    }
    return render(request,'messages/create_message.html',context)