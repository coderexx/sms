from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.paginator import Paginator
from .utils.send_sms import *
from .models import *
from .utils.decorators import role_required


#TODO:Message
@role_required('read_message')
def read_message(request):
    messages = Message.objects.all().order_by('-created_at')
    
    #get query parameters
    student_class_query = request.GET.get('student_class_query', '')
    if student_class_query:
        messages = messages.filter(student_class__id=student_class_query)
        
    # pagination for main_leave
    paginator = Paginator(messages, 50)  # 50 records per page
    page_number = request.GET.get('page')
    messages = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "messages": messages,
        "student_classes": StudentClass.objects.filter(active=True).order_by('number'),
        "student_class_query": int(student_class_query) if student_class_query else None,
        "query_string": query_string
    }
    return render(request,'messages/read_message.html',context)


@role_required('create_message')
def create_message(request):
    if request.method == 'POST':
        student_class = request.POST.get('student_class')
        text = request.POST.get('text')
        segment_count = calculate_sms_segments(text)
        total_sms_sent = 0
        students = Student.objects.filter(student_class_id=student_class, active=True)

        for student in students:
            if student.mob_no:
                success, response = send_sms(student.mob_no, student.name, text)
                if success:
                    total_sms_sent += segment_count
                if not success:
                    messages.error(request, f"❌ Failed to send SMS to {student.name}: {response}")

        # Save message
        Message.objects.create(
            student_class_id=student_class,
            text=text,
            total_sms_count=total_sms_sent
        )
        
        # Always update the latest counter
        latest_counter = SMSCounter.objects.order_by('-created_at').first()
        if not latest_counter:
            # If no counter exists, create the first one
            latest_counter = SMSCounter.objects.create(total_sms_sent=0)
        latest_counter.total_sms_sent += total_sms_sent
        latest_counter.save()

        messages.success(request, "✅ Message was created and sent successfully.")
        return redirect('read_message')  # or your view name

    context = {
        "student_classes": StudentClass.objects.filter(active=True).order_by('number'),
    }
    return render(request, 'messages/create_message.html', context)


@role_required('read_sms_counter')
def read_sms_counter(request):
    all_counters = SMSCounter.objects.all().order_by('-created_at')
    latest_counter = all_counters.first()
    # pagination for all_counters
    paginator = Paginator(all_counters, 50)  # 50 records per page
    page_number = request.GET.get('page')
    all_counters = paginator.get_page(page_number)

    context = {
        "latest_counter": latest_counter,
        "all_counters": all_counters
    }
    return render(request, 'messages/read_sms_counter.html', context)


@role_required('reset_sms_counter')
def reset_sms_counter(request):
    # Create a new counter instance (old one stays in DB)
    SMSCounter.objects.get_or_create(total_sms_sent=0)

    messages.success(request, "✅ SMS counter reset — new counter started.")
    return redirect('read_sms_counter')