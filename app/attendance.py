from django.shortcuts import render, redirect
from .models import Student, Attendance, StudentClass
from datetime import date,datetime
from django.shortcuts import render
from django.contrib import messages
from django.core.paginator import Paginator
from .utils.decorators import role_required

today = date.today()



@role_required('take_attendance')
def take_attendance(request):
    student_class_id = request.GET.get('student_class')
    students = Student.objects.filter(student_class_id=student_class_id)
    # Check if attendance already submitted for this class today
    already_taken = Attendance.objects.filter(
            student__student_class_id=student_class_id,
            date=today
        ).exists()
    if already_taken:
            messages.error(request, "⚠️ Attendance has already been submitted for this class today.")
            return redirect('take_attendance')  # Or render the same page with error


    if request.method == 'POST':
        # Submit attendance
        for student in students:
            is_present = request.POST.get(f"present_{student.id}") == 'on'
            Attendance.objects.create(
                student=student,
                date=today,
                is_present=is_present
            )

        messages.success(request, "✅ Attendance submitted successfully.")
        return redirect('take_attendance')

    return render(request, 'attendance/take.html', {
        'students': students,
        'student_class': int(student_class_id) if student_class_id else None,
        "student_classes": StudentClass.objects.all().order_by('number'),
    })



@role_required('attendance_report')
def attendance_report(request):
    # Get filter values from query params
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            date = today  # fallback if format is wrong
    else:
        date = today
    selected_class = request.GET.get('student_class')

    # Base queryset
    attendances = Attendance.objects.filter(date=date).order_by('student__student_class__number','is_present')

    # Apply filters
    if selected_class:
        attendances = attendances.filter(student__student_class_id=selected_class)
        
    # Get is_present filter
    is_present = request.GET.get('is_present')
    if is_present == 'True':
        attendances = attendances.filter(is_present=True)
    elif is_present == 'False':
        attendances = attendances.filter(is_present=False)

    # Get distinct classes for filter dropdown
    classes = StudentClass.objects.all().order_by('number')

    total = attendances.count()
    
    
    # pagination for main_leave
    paginator = Paginator(attendances, 100)  # 100 records per page
    page_number = request.GET.get('page')
    attendances = paginator.get_page(page_number)
    
    
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        'attendances': attendances,
        'classes': classes,
        'date': date,
        'selected_class': selected_class,
        'total': total,
        'query_string': query_string,
        'is_present': is_present
    }
    return render(request, 'attendance/report.html', context)