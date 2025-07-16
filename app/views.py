from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout,get_user_model,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()
# Create your views here.

def no_permission(request):
    return render(request, 'others/no_permission.html')

def do_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
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
                return redirect("dashboard")
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



@login_required
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
