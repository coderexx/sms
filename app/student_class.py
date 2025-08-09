from datetime import datetime, date
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from .utils.send_sms import *
from .models import *
from django.contrib.auth.decorators import login_required

from .utils.decorators import role_required

# global variables
today = date.today()


#TODO:StudentClass
#read_student_class
@role_required('read_student_class')
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
@role_required('create_student_class')
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
@role_required('update_student_class')
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
@role_required('delete_student_class')
def delete_student_class(request,id):
    student_class = StudentClass.objects.get(id=id)
    messages.success(request,f"{student_class.number} was deleted successfully.")
    return redirect(read_student_class)


#activation_student_class
@role_required('update_student_class')
def activation_student_class(request,id):
    student_class = StudentClass.objects.get(id=id)
    if student_class.active == True:
        student_class.active = False
        if not student_class.inactive_date:
            student_class.inactive_date = today
        messages.success(request,f"class {student_class.number} was deactivation successfully.")
    else:
        student_class.active = True
        messages.success(request,f"class {student_class.number} was activation successfully.")
    student_class.save()
    return redirect(read_student_class)

#shift_down_student_class
@role_required('update_student_class')
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
@role_required('update_student_class')
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