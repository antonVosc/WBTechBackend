from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomerUserAdmin(UserAdmin):
    list_display = ("username", "email", "balance", "is_staff", "is_active")

    fieldsets = UserAdmin.fieldsets + (("Balance", {"fields": ("balance",)}),)
