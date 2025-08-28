from datetime import datetime, date
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db.models.functions import ExtractYear
from app.views import User
from .utils.send_sms import *
from .models import *
from .utils.decorators import role_required


# global variables
today = date.today()

@role_required('dashboard')
def dashboard(request):
    total_active_students = Student.objects.filter(active=True, student_class__active=True).count()
    total_active_teachers = Teacher.objects.filter(active=True).count()

    active_classes = StudentClass.objects.filter(active=True).order_by('number')
    class_data = []

    for cls in active_classes:
        student_count = Student.objects.filter(student_class=cls, active=True).count()
        male_count = Student.objects.filter(student_class=cls, active=True, gender='male').count()
        female_count = Student.objects.filter(student_class=cls, active=True, gender='female').count()
        
        # Today's attendance
        attendance_today = Attendance.objects.filter(student__student_class=cls, date=today)
        present_count = attendance_today.filter(is_present=True).count()
        absent_count = attendance_today.filter(is_present=False).count()
        class_data.append({
            'class': cls,
            'student_count': student_count,
            'male_count': male_count,
            'female_count': female_count,
            'present_count': present_count,
            'absent_count': absent_count,
        })
        
    attendance_data = (
        Attendance.objects.filter(date=today)  # ✅ Only today's records
        .values('date').annotate(present=Count('id', filter=Q(is_present=True)),absent=Count('id', filter=Q(is_present=False)),total=Count('id'))
    )

    context = {
        'total_active_students': total_active_students,
        'total_active_teachers': total_active_teachers,
        'class_data': class_data,
        "attendance_data":attendance_data,
    }

    return render(request, 'admin/dashboard.html', context)



# TODO: Teaching Assignment
@role_required('read_teaching_assignment')
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
    role = request.user.role
    if role and role.modules.filter(name='read_student_self').exists():
        selected_class = Student.objects.filter(user=request.user).first().student_class.id

    queryset = TeachingAssignment.objects.filter(
        date__year=selected_year,
        date__month=selected_month
    ).order_by('-date')

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
@role_required('create_teaching_assignment')
def create_teaching_assignment(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        subject_id = request.POST.get('subject')
        student_class_id = request.POST.get('student_class')

        try:
            teaching_assignment, created = TeachingAssignment.objects.get_or_create(
                teacher_id=teacher_id,
                subject_id=subject_id,
                student_class_id=student_class_id,
                date=today
            )
            if created:
                messages.success(request, f'{teaching_assignment.teacher.name} - {teaching_assignment.subject.name} - {teaching_assignment.student_class.number} Assignment created successfully.')
            else:
                messages.error(request, f'{teaching_assignment.teacher.name} - {teaching_assignment.subject.name} - {teaching_assignment.student_class.number} Assignment already exists.')
        except Exception as e:
            messages.error(request, f'Failed to create assignment: {str(e)}')
        
        return redirect('create_teaching_assignment')

    context = {
        'teachers': Teacher.objects.all().order_by('name'),
        'subjects': Subject.objects.all().order_by('name'),
        'student_classes': StudentClass.objects.all()
    }
    return render(request, 'teaching_assignment/create_teaching_assignment.html', context)



# Delete an assignment
@role_required('delete_teaching_assignment')
def delete_teaching_assignment(request, id):
    assignment = get_object_or_404(TeachingAssignment, id=id)
    assignment.delete()
    return redirect('read_teaching_assignment')




@role_required('create_user')
def create_user(request):
    roles = Role.objects.all().order_by('sn', 'id').exclude(h_name__in=["student", "super_admin"])
    if request.method == 'POST':
        role_id = request.POST.get('role')
        username = request.POST.get('username')
        name = request.POST.get('name')
        mobile_no = request.POST.get('mobile_no')
        picture = request.FILES.get('picture')
        if not all([role_id, username, name, mobile_no]):
            messages.error(request, "All fields are required.")
            return redirect('create_user')
        if Role.objects.get(id=role_id).h_name == "super_admin":
            messages.error(request, "Cannot assign super admin role.")
            return redirect('create_user')
        User.objects.create_user(username=username,password=mobile_no, name=name, mobile_no=mobile_no, role_id=role_id, picture=picture)
        messages.success(request, "User created successfully.")
        return redirect('read_user')
        
    context = {
        'roles': roles
    }
    return render(request, 'user/create_user.html', context)


@role_required('read_user')
def read_user(request):
    users = User.objects.all().order_by('role').exclude(role__h_name="student")
    context = {
        'users': users
    }
    return render(request, 'user/read_user.html', context)

@role_required('update_user')
def update_user(request, id):
    roles = Role.objects.all().order_by('sn', 'id').exclude(h_name__in=["student", "super_admin"])
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        role_id = request.POST.get('role')
        name = request.POST.get('name')
        mobile_no = request.POST.get('mobile_no')
        picture = request.FILES.get('picture')
        if not all([role_id, name, mobile_no]):
            messages.error(request, "All fields are required.")
            return redirect('update_user', id=id)
        if Role.objects.get(id=role_id).h_name == "super_admin":
            messages.error(request, "Cannot assign super admin role.")
            return redirect('update_user', id=id)

        user.role_id = role_id
        user.name = name
        user.mobile_no = mobile_no
        if picture is not None:
            user.picture = picture
        user.save()
        messages.success(request, "User updated successfully.")
        return redirect('read_user')
        
    context = {
        'user': user,
        'roles': roles
    }
    return render(request, 'user/update_user.html', context)

@role_required('update_user')
def reset_user_password(request,id):
    user = get_object_or_404(User, id=id)
    user.set_password(user.mobile_no)
    user.save()
    messages.success(request, "Password reset successfully.")
    return redirect('read_user')
    

@role_required('delete_user')
def delete_user(request,id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('read_user')





    



