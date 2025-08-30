from django.shortcuts import render, redirect
from .models import *
from datetime import date
from django.shortcuts import render
from django.contrib import messages
from django.core.paginator import Paginator
from .utils.decorators import role_required
from django.db.models import Sum, Max, Q
from django.db.models.functions import ExtractYear
#for pdf
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from .utils.send_sms import send_exam_result_sms


today = date.today()
current_year = today.year
current_month = today.month

@role_required('create_exam_result')
def create_exam_result(request):
    student_class_id = request.GET.get('student_class')
    students = Student.objects.filter(student_class_id=student_class_id).order_by('roll_no')


    if request.method == 'POST':
        date = request.POST.get("date")
        subject_id = request.POST.get("subject")
        total_mark = request.POST.get("total_mark")
        remarks = request.POST.get("remarks")
        send_sms = request.POST.get("send_sms")
        if not all([subject_id, total_mark]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('create_exam_result')
        subject = Subject.objects.get(id=subject_id)
        total_sms_sent = 0
        # Submit attendance
        for student in students:
            obtained_mark = request.POST.get(f"obtained_mark_{student.id}")
            ExamResult.objects.create(
                date=date,
                student=student,
                subject_id=subject_id,
                total_mark=total_mark,
                obtained_mark=obtained_mark,
                remarks=remarks
            )
            if send_sms:
                success, response = send_exam_result_sms(student.mob_no, student.name, subject.name, obtained_mark, total_mark, remarks)
                if success:
                    total_sms_sent += 1
                if not success:
                    messages.error(request, f"❌ Failed to send SMS to {student.name}: {response}")
        if send_sms:
            # Always update the latest counter
            latest_counter = SMSCounter.objects.order_by('-created_at').first()
            if not latest_counter:
                # If no counter exists, create the first one
                latest_counter = SMSCounter.objects.create(total_sms_sent=0)
            latest_counter.total_sms_sent += total_sms_sent
            latest_counter.save()

        messages.success(request, f"✅ Exam Result Created successfully. SMS sent: {total_sms_sent}")
        return redirect('create_exam_result')

    return render(request, 'exam/create_exam_result.html', {
        'students': students,
        'student_class': int(student_class_id) if student_class_id else None,
        "student_classes": StudentClass.objects.all().order_by('number'),
        "subjects": Subject.objects.all().order_by('name'),
    })

@role_required('read_exam_result')
def read_exam_result(request):
    results = ExamResult.objects.all().order_by('-date','student__student_class__number','remarks','student__roll_no')

    selected_date = request.GET.get('date')
    selected_subject = request.GET.get('subject')
    selected_class = request.GET.get('student_class')
    if selected_subject:
        results = results.filter(subject_id=selected_subject)
    if selected_class:
        results = results.filter(student__student_class_id=selected_class)
    if selected_date:
        results = results.filter(date=selected_date)

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
        "query_string":query_string,
        "selected_date": selected_date if selected_date else '',
    }
    return render(request, 'exam/read_exam_result.html', context)


@role_required('read_exam_result')
def read_exam_result_pdf(request):
    results = ExamResult.objects.all().order_by('-date','student__student_class__number','remarks','student__roll_no')
    selected_date = request.GET.get('date')
    selected_subject = request.GET.get('subject')
    selected_class = request.GET.get('student_class')
    if selected_subject:
        results = results.filter(subject_id=selected_subject)
    if selected_class:
        results = results.filter(student__student_class_id=selected_class)
    if selected_date:
        results = results.filter(date=selected_date)

    context = {
        "results": results,
        "head":f"Exam Result"
    }
    # Load the HTML template and render it with context data
    template = get_template('pdf/read_exam_result_pdf.html')
    html = template.render(context)

    # Create a response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="result.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    return response

@role_required('read_exam_position')
def read_exam_position(request):
    # Get query parameters
    student_class_id = request.GET.get("student_class")
    selected_month = request.GET.get("selected_month", current_month)
    selected_year = request.GET.get("selected_year", current_year)

    # ----------------------
    # 1. Last Exam Ranking
    # ----------------------
    last_exam_date = ExamResult.objects.filter(student__student_class_id=student_class_id,).aggregate(last_date=Max("date"))["last_date"]
    last_exam_totals = (Student.objects.filter(student_class_id=student_class_id).annotate(total_marks=Sum("examresult__obtained_mark",filter=Q(examresult__date=last_exam_date))).order_by("-total_marks")) if last_exam_date else []
    # Assign last exam rank
    last_exam_ranks = {}
    rank, last_marks = 1, None
    for i, st in enumerate(last_exam_totals, start=1):
        if last_marks is None or st.total_marks < last_marks:
            rank = i
        last_exam_ranks[st.id] = {"rank": rank, "marks": st.total_marks}
        last_marks = st.total_marks
    # ----------------------
    # 2. Monthly Ranking
    # ----------------------
    monthly_totals = (Student.objects.filter(student_class_id=student_class_id).annotate(total_marks=Sum("examresult__obtained_mark",filter=Q(examresult__date__year=selected_year, examresult__date__month=selected_month)),full_marks=Sum("examresult__total_mark",filter=Q(examresult__date__year=selected_year,examresult__date__month=selected_month))).order_by("-total_marks"))
    monthly_ranks = {}
    rank, last_marks = 1, None
    for i, st in enumerate(monthly_totals, start=1):
        if last_marks is None or st.total_marks < last_marks:
            rank = i
        monthly_ranks[st.id] = {"rank": rank, "marks": st.total_marks,"full_marks": st.full_marks}
        last_marks = st.total_marks

    # ----------------------
    # 3. Yearly Ranking
    # ----------------------
    yearly_totals = (Student.objects.filter(student_class_id=student_class_id).annotate(total_marks=Sum("examresult__obtained_mark",filter=Q(examresult__date__year=selected_year))).order_by("-total_marks"))
    yearly_ranks = {}
    rank, last_marks = 1, None
    for i, st in enumerate(yearly_totals, start=1):
        if last_marks is None or st.total_marks < last_marks:
            rank = i
        yearly_ranks[st.id] = {"rank": rank, "marks": st.total_marks}
        last_marks = st.total_marks
    # ----------------------
    # Final response (merge all ranks)
    # ----------------------
    students = Student.objects.filter(student_class_id=student_class_id).order_by('roll_no')
    positions = []
    for st in students:
        positions.append({
            "student_id": st.id,
            "name": st.name,
            "roll_no": st.roll_no,
            "class": st.student_class.number,
            "last_exam_rank": last_exam_ranks.get(st.id, {}).get("rank"),
            "monthly_rank": monthly_ranks.get(st.id, {}).get("rank"),
            "full_marks": monthly_ranks.get(st.id, {}).get("full_marks"),
            "total_marks": monthly_ranks.get(st.id, {}).get("marks"),
            "yearly_rank": yearly_ranks.get(st.id, {}).get("rank"),
            "exam_date": str(last_exam_date) if last_exam_date else None,
        })
    # ✅ Order by monthly_rank (None values go last)
    positions.sort(key=lambda x: (x["monthly_rank"] is None, x["monthly_rank"]))

    years = ExamResult.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct().order_by('-year')

    context = {
        "positions": positions,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'classes': StudentClass.objects.all().order_by('number'),
        'student_class': int(student_class_id) if student_class_id else None,
        'years': years
    }
    return render(request, 'exam/read_exam_position.html', context)


@role_required('read_exam_position')
def read_exam_position_pdf(request):
    # Get query parameters
    student_class_id = request.GET.get("student_class")
    selected_month = request.GET.get("selected_month", current_month)
    selected_year = request.GET.get("selected_year", current_year)

    # ----------------------
    # 1. Last Exam Ranking
    # ----------------------
    last_exam_date = ExamResult.objects.filter(student__student_class_id=student_class_id,).aggregate(last_date=Max("date"))["last_date"]
    last_exam_totals = (Student.objects.filter(student_class_id=student_class_id).annotate(total_marks=Sum("examresult__obtained_mark",filter=Q(examresult__date=last_exam_date))).order_by("-total_marks")) if last_exam_date else []
    # Assign last exam rank
    last_exam_ranks = {}
    rank, last_marks = 1, None
    for i, st in enumerate(last_exam_totals, start=1):
        if last_marks is None or st.total_marks < last_marks:
            rank = i
        last_exam_ranks[st.id] = {"rank": rank, "marks": st.total_marks}
        last_marks = st.total_marks
    # ----------------------
    # 2. Monthly Ranking
    # ----------------------
    monthly_totals = (Student.objects.filter(student_class_id=student_class_id).annotate(total_marks=Sum("examresult__obtained_mark",filter=Q(examresult__date__year=selected_year, examresult__date__month=selected_month)),full_marks=Sum("examresult__total_mark",filter=Q(examresult__date__year=selected_year,examresult__date__month=selected_month))).order_by("-total_marks"))
    monthly_ranks = {}
    rank, last_marks = 1, None
    for i, st in enumerate(monthly_totals, start=1):
        if last_marks is None or st.total_marks < last_marks:
            rank = i
        monthly_ranks[st.id] = {"rank": rank, "marks": st.total_marks,"full_marks": st.full_marks}
        last_marks = st.total_marks

    # ----------------------
    # 3. Yearly Ranking
    # ----------------------
    yearly_totals = (Student.objects.filter(student_class_id=student_class_id).annotate(total_marks=Sum("examresult__obtained_mark",filter=Q(examresult__date__year=selected_year))).order_by("-total_marks"))
    yearly_ranks = {}
    rank, last_marks = 1, None
    for i, st in enumerate(yearly_totals, start=1):
        if last_marks is None or st.total_marks < last_marks:
            rank = i
        yearly_ranks[st.id] = {"rank": rank, "marks": st.total_marks}
        last_marks = st.total_marks
    # ----------------------
    # Final response (merge all ranks)
    # ----------------------
    students = Student.objects.filter(student_class_id=student_class_id).order_by('roll_no')
    positions = []
    for st in students:
        positions.append({
            "student_id": st.id,
            "name": st.name,
            "roll_no": st.roll_no,
            "class": st.student_class.number,
            "last_exam_rank": last_exam_ranks.get(st.id, {}).get("rank"),
            "monthly_rank": monthly_ranks.get(st.id, {}).get("rank"),
            "full_marks": monthly_ranks.get(st.id, {}).get("full_marks"),
            "total_marks": monthly_ranks.get(st.id, {}).get("marks"),
            "yearly_rank": yearly_ranks.get(st.id, {}).get("rank"),
            "exam_date": str(last_exam_date) if last_exam_date else None,
        })
    # ✅ Order by monthly_rank (None values go last)
    positions.sort(key=lambda x: (x["monthly_rank"] is None, x["monthly_rank"]))


    student_class = StudentClass.objects.get(id=student_class_id)
    context = {
        "positions": positions,
        "head":f"Class {student_class.number} - {selected_month}/{selected_year}"
    }
    # Load the HTML template and render it with context data
    template = get_template('pdf/read_exam_position_pdf.html')
    html = template.render(context)

    # Create a response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="position.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    return response