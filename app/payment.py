from datetime import datetime, date
import os
import subprocess
from io import BytesIO
import random
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.views import User
from .utils.decorators import role_required
from .models import *
from django.db.models import Sum, F


# global variables
today = date.today()



def due_table(request):
    student_class_id = request.GET.get('class_id')
    roll_no = request.GET.get('roll_no')
    students = []

    if roll_no:
        students = Student.objects.filter(roll_no=roll_no, active=True)
        
    if student_class_id:
        students = Student.objects.filter(student_class=student_class_id, active=True)

    current_year = datetime.today().year
    current_month = datetime.today().month

    student_data = []

    for student in students:
        join_date = student.join_date or datetime(student.join_date.year, 1, 1).date()
        inactive_date = student.inactive_date or datetime(current_year, current_month, 1).date()

        # Generate year-months from join to current/inactive date
        year_months = []
        year = join_date.year
        month = join_date.month

        while (year < inactive_date.year) or (year == inactive_date.year and month <= inactive_date.month):
            year_months.append((year, month))
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

        # Get paid months as set of (year, month)
        paid = MonthlyPayment.objects.filter(student=student).values_list('year', 'month')
        paid_set = set(paid)

        # Identify unpaid (due) months
        dues = []
        for y, m in year_months:
            if (y, m) not in paid_set:
                dues.append({'year': y, 'month': m})

        student_data.append({
            'id': student.id,
            'name': student.name,
            'roll': student.roll_no,
            'phone': student.mob_no,
            'dues': dues
        })

    return render(request, 'payment/due_table.html', {
        'students': student_data,
        'class_id': student_class_id,
        'student_classes': StudentClass.objects.filter(active=True).order_by('number'),
    })
    
    
def generate_unique_code():
    while True:
        code = random.randint(100000, 999999)
        if not MonthlyPayment.objects.filter(code=code).exists():
            return code
    
@csrf_exempt
def pay_multiple_months(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        months = request.POST.getlist('months[]')  # format: ["2025-01", "2025-02"]
        amount = float(request.POST.get('amount'))
        code = generate_unique_code()
        student = get_object_or_404(Student, id=student_id)

        for ym in months:
            year, month = map(int, ym.split('-'))
            MonthlyPayment.objects.get_or_create(
                student=student,
                year=year,
                month=month,
                code=code,
                defaults={'amount': amount}
            )
        messages.success(request, f"{student.name} Payment was made successfully.")
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)



@login_required
def read_credit(request):
    years = MonthlyPayment.objects.values_list('year', flat=True).distinct().order_by('-year')
    selected_year = request.GET.get('year')
    selected_class = request.GET.get('class_id')
    
    # Auto-select most recent year if not selected
    if not selected_year and years:
        selected_year = int(years[0])
    else:
        selected_year = int(selected_year) if selected_year else None

    selected_class_id = int(selected_class) if selected_class else None

    table_data = []

    if selected_year:
        for month in range(1, 13):
            qs = MonthlyPayment.objects.filter(
                year=selected_year,
                month=month,
            )
            if selected_class_id:
                qs = qs.filter(student__student_class=selected_class_id)

            total = qs.aggregate(total=Sum('amount'))['total'] or 0

            table_data.append({
                'month': calendar.month_name[month],
                'amount': total
            })

    total_amount = sum(row['amount'] for row in table_data)

    context = {
        'total_amount': total_amount,
        'table_data': table_data,
        'selected_year': selected_year,
        'selected_class': selected_class_id,
        'years': years,
        'classes': StudentClass.objects.filter(active=True).order_by('number'),
    }
    return render(request, 'payment/read_credit.html', context)
