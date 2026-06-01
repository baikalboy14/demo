from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Application, Course, Review

User = get_user_model()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_type')
    list_filter = ('course_type',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'start_date', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'user__full_name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'user', 'created_at')


@admin.register(User)
class PortalUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('full_name', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('full_name', 'phone', 'email')}),
    )
