# context_processors.py


def role_modules(request):
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', None)
        if role is not None:
            modules = role.modules.all()
        else:
            modules = []
    else:
        modules = []

    module_names = [module.name for module in modules]
    
    
    # Define module categories
    students = {'create_student', 'read_student'}
    teachers = {'create_teacher', 'read_teacher'}
    attendance = {'take_attendance', 'attendance_report'}
    exam = {'create_exam_result', 'read_exam_result'}
    teaching_assignment = {'create_teaching_assignment', 'read_teaching_assignment'}
    setting = {'read_location','read_school','read_subject','change_password','database',}

    return {
        "module_names": module_names,
        'user_modules': modules,
        'has_students': any(module.name in students for module in modules),
        'has_teachers': any(module.name in teachers for module in modules),
        'has_attendance': any(module.name in attendance for module in modules),
        'has_exam': any(module.name in exam for module in modules),
        'has_setting': any(module.name in setting for module in modules),
        'has_teaching_assignment': any(module.name in teaching_assignment for module in modules),
    }
