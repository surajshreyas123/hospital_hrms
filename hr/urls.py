
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Employee management
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path(
        "employees/<int:pk>/",
        views.employee_profile,
        name="employee_profile",
    ),
    path(
        "employees/<int:pk>/edit/",
        views.employee_edit,
        name="employee_edit",
    ),

    # Attendance
    path(
        "attendance/",
        views.attendance_report,
        name="attendance_report",
    ),

    # Leave management
    path("leaves/", views.leave_list, name="leave_list"),
    path("leaves/apply/", views.leave_create, name="leave_create"),
    path(
        "leaves/<int:pk>/review/",
        views.leave_review,
        name="leave_review",
    ),

    # Birthday calendar
    path(
        "birthdays/",
        views.birthday_calendar,
        name="birthday_calendar",
    ),
    path("roles/", views.role_management, name="role_management"),
    path(
        "roles/edit/<int:role_id>/",
        views.role_management,
        name="edit_role",
    ),
]

