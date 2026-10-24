from django import forms
from django.contrib.auth.models import Group

from .models import Employee, LeaveRequest, Department


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label="Login Username",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter login username",
            "autocomplete": "username",
        }),
    )

    password = forms.CharField(
        label="Login Password",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter login password",
            "autocomplete": "new-password",
        }),
        help_text=(
            "Required for a new account. Leave blank when editing "
            "to keep the current password."
        ),
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        required=True,
    )

    role = forms.ModelChoiceField(
        queryset=Group.objects.all().order_by("name"),
        empty_label="Select Role",
        required=True,
        label="Employee Role",
    )

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "name",
            "email",
            "phone",
            "designation",
            "staff_type",
            "department",
            "joining_date",
            "birthday",
            "salary",
            "status",
        ]
        widgets = {
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee = self.instance

        self.fields["password"].required = (
            not employee.pk or not employee.user_id
        )

        if employee.pk and employee.user_id:
            self.fields["username"].initial = (
                getattr(employee.user, "username", "")
            )
            self.fields["role"].initial = (
                employee.user.groups.order_by("name").first()
            )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        from django.contrib.auth import get_user_model

        User = get_user_model()
        users = User.objects.filter(username__iexact=username)

        if self.instance.pk and self.instance.user_id:
            users = users.exclude(pk=self.instance.user_id)

        if users.exists():
            raise forms.ValidationError(
                "This username is already taken. Choose another."
            )

        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if password and len(password) < 8:
            raise forms.ValidationError(
                "Password must contain at least 8 characters."
            )

        return password


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        data = super().clean()
        start = data.get("start_date")
        end = data.get("end_date")

        if start and end and end < start:
            raise forms.ValidationError(
                "End date cannot be before the start date."
            )

        return data