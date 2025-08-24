from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout,get_user_model,update_session_auth_hash
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .utils.decorators import role_required
import os
from io import BytesIO
import datetime
import subprocess
User = get_user_model()
# Create your views here.

def no_permission(request):
    return render(request, 'others/no_permission.html')

def home(request):
    if request.user.is_authenticated:
        role = request.user.role
        if role and role.modules.filter(name='dashboard').exists():
            return redirect("dashboard")
        if role and role.modules.filter(name='read_student_self').exists():
            return redirect("profile_student",id=request.user.student.id)
        else:
            return render(request, 'others/no_permission.html')
    else:
        return redirect("login")


def do_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            remember_me = request.POST.get("remember_me")  # Get checkbox value
            is_email_valid = User.objects.filter(username=username).exists()
            if not is_email_valid:
                messages.error(request, "Invalid Login Email")
                return redirect("login")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                    # Set session expiry based on "Remember Me"
                if not remember_me:  # If checkbox is NOT checked
                    request.session.set_expiry(0)  # Session expires when browser closes
                else:
                    request.session.set_expiry(1209600)  # 2 weeks (in seconds)
                return redirect("home")
            else:
                messages.error(request, "Invalid Login Password")
                return redirect("login")
        except:
            messages.error(request, "Invalid Login Details")
            return redirect("login")
    else:
        return render(request, 'login.html')
        
        
def do_logout(request):
    logout(request)  # Correct way to log out the user
    return redirect("login")  # Redirect to the login page



@role_required('change_password')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        user = request.user

        errors = []

        if not user.check_password(old_password):
            errors.append("Old password is incorrect.")

        if new_password1 != new_password2:
            errors.append("New passwords do not match.")

        try:
            validate_password(new_password1, user)
        except ValidationError as ve:
            errors.extend(ve.messages)

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)  # keeps the user logged in
            messages.success(request, "Password changed successfully.")
            return redirect('change_password')

    return render(request, 'setting/change_password.html')


def documentation(request):
    return render(request, 'others/documentation.html')




#XXX: Database Backup
@role_required('database')
def database(request):
    return render(request, 'setting/database.html')

@role_required('database')
def backup_database(request):
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST', '127.0.0.1')
    db_port = os.environ.get('DB_PORT', '3306')

    filename = f"vomms_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    # Use BytesIO instead of saving to disk
    buffer = BytesIO()

    # Build the command
    cmd = [
        'mysqldump',
        '-h', db_host,
        '-P', db_port,
        '-u', db_user,
        f'-p{db_password}',  # Note: this is insecure in subprocess, use Popen with stdin for better security
        db_name
    ]

    # Run the command and write output to buffer
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        return HttpResponse(f"Backup failed: {err.decode()}", status=500)

    buffer.write(out)
    buffer.seek(0)

    # Return the in-memory file as a response
    return FileResponse(buffer, as_attachment=True, filename=filename)

@role_required('database')
def restore_database(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']
        temp_path = os.path.join(os.getcwd(), 'temp_restore.sql')

        with open(temp_path, 'wb+') as f:
            for chunk in upload.chunks():
                f.write(chunk)

        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST', '127.0.0.1')
        db_port = os.environ.get('DB_PORT', '3306')

        cmd = f'mysql -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} < "{temp_path}"'
        subprocess.run(cmd, shell=True, check=True)

        os.remove(temp_path)  # Cleanup uploaded file
        messages.success(request, 'Database restored successfully.')
        return redirect('database')
    messages.error(request, 'No file uploaded or invalid request.')
    return redirect('database')
