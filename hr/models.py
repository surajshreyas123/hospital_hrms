
from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        permissions = [
            ("view_dashboard", "Can view the HRMS dashboard"),
            ("view_employee_pages", "Can view employee pages"),
            ("manage_employee_pages", "Can add and edit employees"),
            ("view_attendance_pages", "Can view attendance pages"),
            ("apply_leave_requests", "Can apply for leave"),
            ("view_leave_pages", "Can view leave requests"),
            ("approve_leave_requests", "Can approve or reject leave requests"),
            ("view_birthday_calendar", "Can view the birthday calendar"),
        ]

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        ON_LEAVE = "ON_LEAVE", "On Leave"

    class StaffType(models.TextChoices):
        DOCTOR = "DOCTOR", "Doctor"
        DUTY_DOCTOR = "DUTY_DOCTOR", "Duty Doctor"
        NURSE = "NURSE", "Nurse"
        TECHNICIAN = "TECHNICIAN", "Technician"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        SUPPORT = "SUPPORT", "Support Staff"
        OTHER = "OTHER", "Other"

    # Linked Django login account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
    )

    name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20)

    designation = models.CharField(max_length=100)

    staff_type = models.CharField(
        max_length=20,
        choices=StaffType.choices,
        default=StaffType.OTHER,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
    )

    # Reporting hierarchy: the employee's direct manager
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
        verbose_name="Reports To",
    )

    joining_date = models.DateField()

    birthday = models.DateField(
        null=True,
        blank=True,
    )

    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class Shift(models.Model):
    name = models.CharField(max_length=50)

    start_time = models.TimeField()

    end_time = models.TimeField()

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="shifts",
    )

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.name


class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    date = models.DateField()

    check_in = models.DateTimeField(
        null=True,
        blank=True,
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
    )

    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="attendance_records",
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Check-in Latitude",
    )

    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Check-in Longitude",
    )

    ip_address = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Check-in IP Address",
    )

    verification_source = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Verification Method",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="unique_employee_attendance_per_day",
            )
        ]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee} - {self.date}"

    @property
    def hours_worked(self):
        if self.check_in and self.check_out:
            diff = self.check_out - self.check_in
            total_seconds = int(diff.total_seconds())
            if total_seconds < 0:
                return "—"
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "—"


class LeaveRequest(models.Model):
    class LeaveStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="leave_requests",
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reviewed_leave_requests",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.employee} - {self.start_date}"


class HospitalSetting(models.Model):
    class VerificationMode(models.TextChoices):
        WIFI_ONLY = "WIFI_ONLY", "Hospital Wi-Fi Only"
        GPS_ONLY = "GPS_ONLY", "GPS Geofence Only"
        WIFI_OR_GPS = "WIFI_OR_GPS", "Either Hospital Wi-Fi OR GPS"
        BOTH = "BOTH", "Both Wi-Fi AND GPS Required"

    hospital_name = models.CharField(
        max_length=200,
        default="Hospital Campus",
    )

    verification_mode = models.CharField(
        max_length=20,
        choices=VerificationMode.choices,
        default=VerificationMode.WIFI_ONLY,
        help_text="Verification requirement for marking attendance",
    )

    wifi_name = models.CharField(
        max_length=150,
        default="Hospital Wi-Fi",
        blank=True,
        help_text="Display name of the Hospital Wi-Fi network",
    )

    allowed_wifi_ips = models.TextField(
        default="127.0.0.1, ::1, localhost, 192.168.*, 10.*",
        help_text="Comma/newline-separated list of allowed Wi-Fi public IPs, local subnets (e.g. 192.168.1.*, 10.0.*), or CIDR",
    )

    latitude = models.FloatField(
        default=12.9716,
        help_text="Hospital latitude coordinate",
    )

    longitude = models.FloatField(
        default=77.5946,
        help_text="Hospital longitude coordinate",
    )

    radius_meters = models.IntegerField(
        default=500,
        help_text="Allowed radius in meters for staff check-in (e.g. 500m)",
    )

    is_geofence_enabled = models.BooleanField(
        default=True,
        help_text="Enforce GPS location check during attendance",
    )

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"{self.hospital_name} ({self.radius_meters}m radius)"

