from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .utils.decorators import role_required
from .models import *






#TODO:Location
#read_location
@role_required('read_location')
def read_location(request):
    locations = Location.objects.all().order_by('name')
    
    # pagination for main_leave
    paginator = Paginator(locations, 50)  # 50 records per page
    page_number = request.GET.get('page')
    locations = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "locations":locations,
        "query_string": query_string
    }
    return render(request,'setting/read_location.html',context)

#create_location
@role_required('create_location')
def create_location(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Location.objects.create(name=name)
            messages.success(request, 'Location created successfully.')
            return redirect(read_location)
        else:
            messages.error(request, 'Invalid location name.')
    context = {

    }
    return render(request,'setting/create_location.html',context)

#update_location
@role_required('update_location')
def update_location(request,id):
    location = get_object_or_404(Location, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            location.name = name
            location.save()
            messages.success(request, 'Location updated successfully.')
            return redirect(read_location)
        else:
            messages.error(request, 'Invalid location name.')
    context = {
        "location": location
    }
    return render(request,'setting/update_location.html',context)

#delete_location
@role_required('delete_location')
def delete_location(request,id):
    location = Location.objects.get(id=id)
    messages.success(request,f"{location.name} was deleted successfully.")
    return redirect(read_location)



#TODO:School
#read_location
@role_required('read_school')
def read_school(request):
    schools = School.objects.all().order_by('name')
    
    # pagination for main_leave
    paginator = Paginator(schools, 50)  # 50 records per page
    page_number = request.GET.get('page')
    schools = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "schools":schools,
        "query_string": query_string
    }
    return render(request,'setting/read_school.html',context)

#create_school
@role_required('create_school')
def create_school(request):
    locations = Location.objects.all().order_by('name')
    if request.method == 'POST':
        name = request.POST.get('name')
        location_id = request.POST.get('location')
        if name and location_id:
            location = get_object_or_404(Location, id=location_id)
            School.objects.create(name=name, location=location)
            messages.success(request, 'School created successfully.')
            return redirect(read_school)
        else:
            messages.error(request, 'Invalid school name or location.')
    context = {
        "locations": locations
    }
    return render(request,'setting/create_school.html',context)

#update_school
@role_required('update_school')
def update_school(request,id):
    school = get_object_or_404(School, id=id)
    locations = Location.objects.all().order_by('name')
    if request.method == 'POST':
        name = request.POST.get('name')
        location_id = request.POST.get('location')
        if name and location_id:
            location = get_object_or_404(Location, id=location_id)
            school.name = name
            school.location = location
            school.save()
            messages.success(request, 'School updated successfully.')
            return redirect(read_school)
        else:
            messages.error(request, 'Invalid school name or location.')
    context = {
        "school": school,
        "locations": locations
    }
    return render(request,'setting/update_school.html',context)

#delete_school
@role_required('delete_school')
def delete_school(request,id):
    school = School.objects.get(id=id)
    messages.success(request,f"{school.name} was deleted successfully.")
    return redirect(read_school)



#TODO:Subject
#read_subject
@role_required('read_subject')
def read_subject(request):
    subjects = Subject.objects.all().order_by('name')
    
    # pagination for main_leave
    paginator = Paginator(subjects, 50)  # 50 records per page
    page_number = request.GET.get('page')
    subjects = paginator.get_page(page_number)
    # Handle query parameters for pagination
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        query_dict.pop('page')
    query_string = query_dict.urlencode()
    context = {
        "subjects":subjects,
        "query_string": query_string
    }
    return render(request,'setting/read_subject.html',context)

#create_subject
@role_required('create_subject')
def create_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Subject.objects.create(name=name)
            messages.success(request, 'Subject created successfully.')
            return redirect(read_subject)
        else:
            messages.error(request, 'Invalid subject name.')
    context = {

    }
    return render(request,'setting/create_subject.html',context)

#update_subject
@role_required('update_subject')
def update_subject(request,id):
    subject = get_object_or_404(Subject, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            subject.name = name
            subject.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect(read_subject)
        else:
            messages.error(request, 'Invalid subject name.')
    context = {
        "subject": subject
    }
    return render(request,'setting/update_subject.html',context)

#delete_subject
@role_required('delete_subject')
def delete_subject(request,id):
    subject = Subject.objects.get(id=id)
    messages.success(request,f"{subject.name} was deleted successfully.")
    return redirect(read_subject)