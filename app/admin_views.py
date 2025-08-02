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
from django.db.models.functions import ExtractYear

from app.views import User
from .utils.decorators import role_required
from .utils.send_sms import *
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



# TODO: Teaching Assignment
def read_teaching_assignment(request):
    years = TeachingAssignment.objects.annotate(
        year=ExtractYear('date')
    ).values_list('year', flat=True).distinct().order_by('-year')
    today = datetime.now()
    selected_year = int(request.GET.get('year', today.year))
    selected_month = int(request.GET.get('month', today.month))
    selected_teacher = request.GET.get('teacher')
    selected_subject = request.GET.get('subject')
    selected_class = request.GET.get('student_class')

    queryset = TeachingAssignment.objects.filter(
        date__year=selected_year,
        date__month=selected_month
    )

    if selected_teacher:
        queryset = queryset.filter(teacher_id=selected_teacher)
    if selected_subject:
        queryset = queryset.filter(subject_id=selected_subject)
    if selected_class:
        queryset = queryset.filter(student_class_id=selected_class)

    total = queryset.count()
    # pagination for main_leave
    paginator = Paginator(queryset, 50)  # 50 records per page
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()

    context = {
        'teaching_assignments': queryset,
        'total': total,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_teacher': int(selected_teacher) if selected_teacher else '',
        'selected_subject': int(selected_subject) if selected_subject else '',
        'selected_class': int(selected_class) if selected_class else '',

        'teachers': Teacher.objects.all().order_by('name'),
        'subjects': Subject.objects.all().order_by('name'),
        'classes': StudentClass.objects.all().order_by('number'),
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'years': years,
        'query_string': query_string
    }
    return render(request, 'teaching_assignment/read_teaching_assignment.html', context)


# Create new assignment
def create_teaching_assignment(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        subject_id = request.POST.get('subject')
        student_class_id = request.POST.get('student_class')
        date = request.POST.get('date')

        try:
            TeachingAssignment.objects.create(
                teacher_id=teacher_id,
                subject_id=subject_id,
                student_class_id=student_class_id,
                date=date
            )
            messages.success(request, 'Assignment created successfully.')
        except Exception as e:
            messages.error(request, f'Failed to create assignment: {str(e)}')
        
        return redirect('read_teaching_assignment')

    context = {
        'teachers': Teacher.objects.all().order_by('name'),
        'subjects': Subject.objects.all().order_by('name'),
        'student_classes': StudentClass.objects.all()
    }
    return render(request, 'teaching_assignment/create_teaching_assignment.html', context)



# Delete an assignment
def delete_teaching_assignment(request, id):
    assignment = get_object_or_404(TeachingAssignment, id=id)
    assignment.delete()
    return redirect('read_teaching_assignment')










    



