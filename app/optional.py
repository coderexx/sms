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