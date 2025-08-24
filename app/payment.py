from datetime import datetime, date
import random
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from app.views import User
from .utils.decorators import role_required
from .models import *
from django.db.models import Sum, F
from django.db.models.functions import ExtractMonth, ExtractYear


# global variables
today = date.today()


@role_required('due_table')
def due_table(request):
    student_class_id = request.GET.get('class_id')
    roll_no = request.GET.get('roll_no')
    students = []

    if roll_no:
        students = Student.objects.filter(roll_no=roll_no, active=True).order_by('name')
    elif student_class_id:
        students = Student.objects.filter(student_class=student_class_id, active=True).order_by('name')

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    student_data = []

    for student in students:
        join_date = student.join_date or date(current_year, 1, 1)

        # Billing starts from join month (postpaid), so include it in calculation
        start_year = join_date.year
        start_month = join_date.month

        # Calculate end date: previous month of current date
        # Because postpaid: current month is not yet due
        if current_month == 1:
            end_year = current_year - 1
            end_month = 12
        else:
            end_year = current_year
            end_month = current_month - 1

        # If student became inactive earlier, limit due to inactive_date
        inactive_date = student.inactive_date
        if inactive_date:
            if inactive_date.year < end_year or (inactive_date.year == end_year and inactive_date.month < end_month):
                end_year = inactive_date.year
                end_month = inactive_date.month

        # Generate due months between start and end
        year_months = []
        y, m = start_year, start_month
        while (y < end_year) or (y == end_year and m <= end_month):
            year_months.append((y, m))
            if m == 12:
                y += 1
                m = 1
            else:
                m += 1

        # Fetch paid months
        paid_set = set(MonthlyPayment.objects.filter(student=student).values_list('year', 'month'))

        # Filter out already paid months
        dues = [{'year': y, 'month': m} for y, m in year_months if (y, m) not in paid_set]

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
@role_required('make_payment')
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



@role_required('read_credit')
def read_credit(request):
    # Get distinct years from payment_date
    years = MonthlyPayment.objects.annotate(payment_year=ExtractYear('payment_date')) \
        .values_list('payment_year', flat=True).distinct().order_by('-payment_year')

    selected_year = request.GET.get('year')
    selected_class = request.GET.get('class_id')

    if not selected_year and years:
        selected_year = int(years[0])
    else:
        selected_year = int(selected_year) if selected_year else None

    selected_class_id = int(selected_class) if selected_class else None

    table_data = []

    if selected_year:
        for month in range(1, 13):
            qs = MonthlyPayment.objects.annotate(
                payment_year=ExtractYear('payment_date'),
                payment_month=ExtractMonth('payment_date')
            ).filter(
                payment_year=selected_year,
                payment_month=month
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
