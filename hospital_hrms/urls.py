
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # All Hospital HRMS pages
    path("", include("hr.urls")),

    # Login, logout, password reset and related pages
    path("accounts/", include("django.contrib.auth.urls")),
]
