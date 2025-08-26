from django.urls import path
from .views import *
from .setting import *
from .admin_views import *
from .payment import *
from .message import *
from .information import *
from .profile import *
from .student_class import *
from .attendance import *
from .exam import *
urlpatterns = [
    
    path('', do_login, name='login'),
    path('logout', do_logout, name='logout'),
    path('no_permission', no_permission, name='no_permission'),
    path('documentation', documentation, name='documentation'),
    # database
    path('database', database, name='database'),
    path('backup_database', backup_database, name='backup_database'),
    path('restore_database', restore_database, name='restore_database'),
    # change password
    path('change_password', change_password, name='change_password'),

    
    
    # TODO: Admin
    path('home', home, name='home'),
    path('dashboard', dashboard, name='dashboard'),
    
     
    #TODO:Student
    path('create_student', create_student, name='create_student'),
    path('read_student', read_student, name='read_student'),
    path('read_inactive_student', read_inactive_student, name='read_inactive_student'),
    path('read_student_pdf', read_student_pdf, name='read_student_pdf'),
    path('read_student_pdf/<str:inactive>', read_student_pdf, name='read_student_pdf'),
    path('update_student/<int:id>', update_student, name='update_student'),
    path('delete_student/<int:id>', delete_student, name='delete_student'),
    path('reset_student_password/<int:id>', reset_student_password, name='reset_student_password'),
    path('activation_student/<int:id>', activation_student, name='activation_student'),
    #TODO:Teacher
    path('create_teacher', create_teacher, name='create_teacher'),
    path('read_teacher', read_teacher, name='read_teacher'),
    path('read_inactive_teacher', read_inactive_teacher, name='read_inactive_teacher'), 
    path('read_teacher_pdf', read_teacher_pdf, name='read_teacher_pdf'),
    path('read_teacher_pdf/<str:inactive>', read_teacher_pdf, name='read_teacher_pdf'),
    path('update_teacher/<int:id>', update_teacher, name='update_teacher'),
    path('delete_teacher/<int:id>', delete_teacher, name='delete_teacher'),
    path('activation_teacher/<int:id>', activation_teacher, name='activation_teacher'),
    #TODO:Student Class
    path('create_student_class', create_student_class, name='create_student_class'),
    path('read_student_class', read_student_class, name='read_student_class'),
    path('shift_down_student_class', shift_down_student_class, name='shift_down_student_class'),
    path('shift_up_student_class', shift_up_student_class, name='shift_up_student_class'),
    path('update_student_class/<int:id>', update_student_class, name='update_student_class'),
    path('delete_student_class/<int:id>', delete_student_class, name='delete_student_class'),
    path('activation_student_class/<int:id>', activation_student_class, name='activation_student_class'),
    #TODO:Location
    path('create_location', create_location, name='create_location'),
    path('read_location', read_location, name='read_location'),
    path('update_location/<int:id>', update_location, name='update_location'),
    path('delete_location/<int:id>', delete_location, name='delete_location'),
    #TODO:School
    path('create_school', create_school, name='create_school'),
    path('read_school', read_school, name='read_school'),
    path('update_school/<int:id>', update_school, name='update_school'),
    path('delete_school/<int:id>', delete_school, name='delete_school'),
    #TODO:Subject
    path('create_subject', create_subject, name='create_subject'),
    path('read_subject', read_subject, name='read_subject'),
    path('update_subject/<int:id>', update_subject, name='update_subject'),
    path('delete_subject/<int:id>', delete_subject, name='delete_subject'),
    
    
    #TODO:Profile
    path('profile_student/<int:id>', profile_student, name='profile_student'),
    path('profile_teacher/<int:id>', profile_teacher, name='profile_teacher'),
    
    #TODO:Teaching Assignment
    path('create_teaching_assignment', create_teaching_assignment, name='create_teaching_assignment'),
    path('read_teaching_assignment', read_teaching_assignment, name='read_teaching_assignment'),
    path('delete_teaching_assignment/<int:id>', delete_teaching_assignment, name='delete_teaching_assignment'),
    
    
    #TODO:Message
    path('create_message', create_message, name='create_message'),
    path('read_message', read_message, name='read_message'),
    path('reset_sms_counter', reset_sms_counter, name='reset_sms_counter'),
    path('read_sms_counter', read_sms_counter, name='read_sms_counter'),
    
    
    # TODO: Payment
    path('due_table/',due_table, name='due_table'),
    path('pay_multiple/',pay_multiple_months, name='pay_multiple'),
    path('read_credit/',read_credit, name='read_credit'),
    
    # TODO: Attendance
    path('take_attendance', take_attendance, name='take_attendance'),
    path('attendance_report', attendance_report, name='attendance_report'),

    # TODO: Exam
    path('create_exam_result', create_exam_result, name='create_exam_result'),
    path('read_exam_result', read_exam_result, name='read_exam_result'),
    path('read_exam_result_pdf', read_exam_result_pdf, name='read_exam_result_pdf'),
    path('read_exam_position', read_exam_position, name='read_exam_position'),
    path('read_exam_position_pdf', read_exam_position_pdf, name='read_exam_position_pdf'),


    #TODO:User
    path('create_user', create_user, name='create_user'),
    path('read_user', read_user, name='read_user'),
    path('update_user/<int:id>', update_user, name='update_user'),
    path('reset_user_password/<int:id>', reset_user_password, name='reset_user_password'),
    path('delete_user/<int:id>', delete_user, name='delete_user'),



    # TODO:setting
]

