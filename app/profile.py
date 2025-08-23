from datetime import datetime, date
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .models import *
from django.db.models.functions import ExtractYear
from django.db.models import Sum, Max

from django.contrib.auth.decorators import login_required
from .utils.decorators import role_required


# global variables
today = date.today()


#student profile
@login_required
def profile_student(request,id):
    # check if the user has permission to read member profile
    role = request.user.role
    if role and role.modules.filter(name='read_student').exists():
        if not Student.objects.filter(id=id).exists():
            messages.error(request, "Student Doesn't Exist")
            return redirect('home')
    elif role and role.modules.filter(name='read_student_self').exists():
        if not Student.objects.filter(id=id, user=request.user).exists():
            messages.error(request, "Student Doesn't Exist")
            return redirect('home')
    else:
        return render(request, 'others/no_permission.html')
    student = Student.objects.get(id=id)
    payments = student.monthly_payments.order_by('-year', '-month')

    current_year = today.year
    current_month = today.month
    # Determine start date from join_date
    join_date = student.join_date or date(current_year, 1, 1)
    start_year = join_date.year
    start_month = join_date.month

    # End month is previous month (postpaid logic)
    if current_month == 1:
        end_year = current_year - 1
        end_month = 12
    else:
        end_year = current_year
        end_month = current_month - 1
    
    # if student_class is inactive, adjust end year/month
    if student.student_class.inactive_date:
        inactive_year = student.student_class.inactive_date.year
        inactive_month = student.student_class.inactive_date.month
        if (inactive_year, inactive_month) < (end_year, end_month):
            end_year = inactive_year
            end_month = inactive_month
    

    # If student is inactive, adjust end year/month
    if student.inactive_date:
        inactive_year = student.inactive_date.year
        inactive_month = student.inactive_date.month
        if (inactive_year, inactive_month) < (end_year, end_month):
            end_year = inactive_year
            end_month = inactive_month

    # Build list of (year, month) from join to end
    year_months = []
    y, m = start_year, start_month
    while (y < end_year) or (y == end_year and m <= end_month):
        year_months.append((y, m))
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1

    # Get paid months
    paid_months = set(MonthlyPayment.objects.filter(student=student).values_list('year', 'month'))

    # Identify due months
    due_months = [(y, m) for y, m in year_months if (y, m) not in paid_months]
            
            
    
            
    # TODO:Attendance
    attendance_month = int(request.GET.get('attendance_month', today.month))
    attendance_year = int(request.GET.get('attendance_year', today.year))
    attendances = Attendance.objects.filter(student=student, date__year=attendance_year, date__month=attendance_month)

    # Dictionary like {day: True/False}
    attendance_status_by_day = {a.date.day: a.is_present for a in attendances}

    cal = calendar.Calendar()
    attendance_days = cal.itermonthdays(attendance_year, attendance_month)
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weeks = []
    week = []

    for day in attendance_days:
        week.append(day)
        if len(week) == 7:
            weeks.append(week)
            week = []

    # if the last week is not full
    if week:
        while len(week) < 7:
            week.append(0)
        weeks.append(week)

    years = Attendance.objects.filter(student=student).annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct().order_by('-year')




    # TODO: Exam Result Position
    exam_results = ExamResult.objects.filter(student=student).order_by('-date','-created_at')
    # Step 1: Get all students in the same class
    student_class = student.student_class  # assuming you have a field `student_class` in Student model
    # Step 2: Get total marks of all students in this class for current year
    yearly_scores = (ExamResult.objects.filter(student__student_class=student_class,date__year=today.year).values('student').annotate(total=Sum('obtained_mark')).order_by('-total'))
    # Step 3: Find this student's position in their class
    yearly_position = None
    rank = 1
    for s in yearly_scores:
        if s['student'] == student.id:
            yearly_position = rank
            break
        rank += 1
    # Step 4: Get this student's own total score
    yearly_score = (ExamResult.objects.filter(student=student,date__year=today.year).aggregate(total=Sum('obtained_mark'))['total'] or 0)

    # XXX:Step 1: Monthly Position
    # Step 2: Get total marks of all students in this class for current month
    monthly_scores = (yearly_scores.filter(date__month=today.month).values('student').annotate(total=Sum('obtained_mark')).order_by('-total')  # highest first
    )
    # Step 3: Find this student's position in their class
    monthly_position = None
    rank = 1
    for s in monthly_scores:
        if s['student'] == student.id:
            monthly_position = rank
            break
        rank += 1
    # Step 4: Get this student's own total score
    monthly_score = (ExamResult.objects.filter(student=student,date__year=today.year,date__month=today.month).aggregate(total=Sum('obtained_mark'))['total'] or 0)

    #XXX: last exam position
    # Step 1: Find the latest exam date for this student's class
    last_exam_date = (ExamResult.objects.filter(student__student_class=student.student_class).aggregate(latest=Max('date'))['latest'])
    # Step 2: Get total marks of all students in this class for current month
    last_scores = (ExamResult.objects.filter(student__student_class=student.student_class, date=last_exam_date).values('student').annotate(total=Sum('obtained_mark')).order_by('-total'))
    # Step 3: Find this student's position in their class
    last_position = None
    rank = 1
    for s in last_scores:
        if s['student'] == student.id:
            last_position = rank
            break
        rank += 1
    # Step 4: Get this student's own total score
    last_score = (ExamResult.objects.filter(student=student,date=last_exam_date).aggregate(total=Sum('obtained_mark'))['total'] or 0)


    context = {
        "student":student,
        "exam_results":exam_results,
        "payments":payments,
        "due_months":due_months,
        'attendance_days': attendance_days,
        'attendance_status_by_day': attendance_status_by_day,
        'attendance_month': attendance_month,
        'attendance_year': attendance_year,
        'weekday_names': weekday_names,
        'weeks': weeks,
        'years': years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        "monthly_score": monthly_score,
        "monthly_position": monthly_position,
        "yearly_score": yearly_score,
        "yearly_position": yearly_position,
        "last_score": last_score,
        "last_position": last_position,
    }
    return render(request,'profile/student_profile.html',context)

#teacher profile
@role_required('read_teacher')
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
    
    