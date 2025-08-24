from django.shortcuts import render, redirect
from .models import *
from datetime import date
from django.shortcuts import render
from django.contrib import messages
from django.core.paginator import Paginator
from .utils.decorators import role_required

today = date.today()

@role_required('create_exam_result')
def create_exam_result(request):
    student_class_id = request.GET.get('student_class')
    students = Student.objects.filter(student_class_id=student_class_id)


    if request.method == 'POST':
        subject_id = request.POST.get("subject")
        total_mark = request.POST.get("total_mark")
        remarks = request.POST.get("remarks")
        if not all([subject_id, total_mark]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('create_exam_result')
        # Submit attendance
        for student in students:
            obtained_mark = request.POST.get(f"obtained_mark_{student.id}")
            ExamResult.objects.create(
                date=today,
                student=student,
                subject_id=subject_id,
                total_mark=total_mark,
                obtained_mark=obtained_mark,
                remarks=remarks
            )

        messages.success(request, "✅ Exam Result Created successfully.")
        return redirect('create_exam_result')

    return render(request, 'exam/create_exam_result.html', {
        'students': students,
        'student_class': int(student_class_id) if student_class_id else None,
        "student_classes": StudentClass.objects.all().order_by('number'),
        "subjects": Subject.objects.all().order_by('name'),
    })

@role_required('read_exam_result')
def read_exam_result(request):
    results = ExamResult.objects.all().order_by('-date')
    
    selected_subject = request.GET.get('subject')
    selected_class = request.GET.get('student_class')
    if selected_subject:
        results = results.filter(subject_id=selected_subject)
    if selected_class:
        results = results.filter(student__student_class_id=selected_class)


    # pagination for main_leave
    paginator = Paginator(results, 100)  # 50 records per page
    page_number = request.GET.get('page')
    results = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "results": results,
        'selected_subject': int(selected_subject) if selected_subject else '',
        'selected_class': int(selected_class) if selected_class else '',
        'subjects': Subject.objects.all().order_by('name'),
        'classes': StudentClass.objects.all().order_by('number'),
        "query_string":query_string
    }
    return render(request, 'exam/read_exam_result.html', context)