from datetime import datetime, date
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models.functions import ExtractYear


# global variables
today = date.today()


#student profile
@login_required
def profile_student(request,id):
    student = Student.objects.get(id=id)
    payments = student.monthly_payments.order_by('-year', '-month')

    # Get list of paid months
    paid_months = {(p.year, p.month) for p in payments}

    # Assume from join date till today
    current_year = date.today().year
    current_month = date.today().month
    due_months = []

    year = student.join_date.year
    month = student.join_date.month

    while (year, month) <= (current_year, current_month):
        if (year, month) not in paid_months:
            due_months.append((year, month))
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    context = {
        "student":student,
        "payments":payments,
        "due_months":due_months
    }
    return render(request,'profile/student_profile.html',context)

#teacher profile
@login_required
def profile_teacher(request,id):
    teacher = get_object_or_404(Teacher, id=id)

    # Get filter values from query params
    today = datetime.now()
    selected_year = int(request.GET.get('year', today.year))
    selected_month = int(request.GET.get('month', today.month))
    selected_subject = request.GET.get('subject')
    selected_class = request.GET.get('student_class')

    # Base queryset
    assignments = TeachingAssignment.objects.filter(teacher=teacher).order_by('-date','-created_at')

    # Apply filters
    if selected_year:
        assignments = assignments.filter(date__year=selected_year)
    if selected_month:
        assignments = assignments.filter(date__month=selected_month)
    if selected_subject:
        assignments = assignments.filter(subject_id=selected_subject)
    if selected_class:
        assignments = assignments.filter(student_class_id=selected_class)

    # Get distinct years for filter dropdown
    years = TeachingAssignment.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct().order_by('-year')
    
    total = assignments.count()
    context = {
        'teacher': teacher,
        'teaching_assignments': assignments,
        'total': total,
        'years': years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'subjects': Subject.objects.all().order_by('name'),
        'student_classes': StudentClass.objects.all().order_by('number'),
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_subject': int(selected_subject) if selected_subject else '',
        'selected_class': int(selected_class) if selected_class else '',
    }
    return render(request,'profile/teacher_profile.html',context)
    
    