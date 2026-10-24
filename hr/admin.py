
from django.contrib import admin
from .models import (
    Department,
    Employee,
    Shift,
    Attendance,
    LeaveRequest,
    HospitalSetting,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "name",
        "designation",
        "department",
        "status",
    )
    list_filter = ("department", "status")
    search_fields = ("employee_id", "name", "email")


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "start_time", "end_time")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "check_in",
        "check_out",
        "verification_source",
        "ip_address",
    )
    list_filter = ("date", "shift", "verification_source")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "start_date",
        "end_date",
        "status",
    )
    list_filter = ("status",)


@admin.register(HospitalSetting)
class HospitalSettingAdmin(admin.ModelAdmin):
    list_display = (
        "hospital_name",
        "verification_mode",
        "wifi_name",
        "radius_meters",
        "is_geofence_enabled",
    )
    fields = (
        "hospital_name",
        "verification_mode",
        "wifi_name",
        "allowed_wifi_ips",
        "latitude",
        "longitude",
        "radius_meters",
        "is_geofence_enabled",
    )
