from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

def role_required(module_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                role = request.user.role
                if role and role.modules.filter(name=module_name).exists():
                    return view_func(request, *args, **kwargs)
            else:
                return redirect('login')
            return render(request, 'others/no_permission.html')
        return wrapper
    return decorator
