from django.contrib import admin
from .models import CustomUser, Course, Enrollment, Feedback, CourseMaterial

# Custom admin configuration for CustomUser model
class CustomUserAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('username', 'email', 'full_name', 'role', 'is_active')
    # Filters available in the admin list view
    list_filter = ('role', 'is_active', 'date_joined')
    # Fields to search in the admin list view
    search_fields = ('username', 'email', 'full_name')
   
    ordering = ('-date_joined',)


class CourseAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('title', 'instructor', 'description')
    # Fields to search in the admin list view
    search_fields = ('title', 'description', 'instructor__username', 'instructor__full_name')
    # Filters available in the admin list view
    list_filter = ('instructor',)
    
    ordering = ('title',)

# Custom admin configuration for Enrollment model
class EnrollmentAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('student', 'course', 'date_enrolled')
    # Fields to search in the admin list view
    search_fields = ('student__username', 'student__full_name', 'course__title')
    # Filters available in the admin list view
    list_filter = ('course', 'student')
    
    ordering = ('-date_enrolled',)

# Custom admin configuration for Feedback model
class FeedbackAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('course', 'student', 'text', 'created_at')
    # Fields to search in the admin list view
    search_fields = ('student__username', 'student__full_name', 'course__title', 'text')
    # Filters available in the admin list view
    list_filter = ('course', 'student', 'created_at')
    
    ordering = ('-created_at',)

# Custom admin configuration for CourseMaterial model
class CourseMaterialAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('course', 'name', 'file')
    # Fields to search in the admin list view
    search_fields = ('course__title', 'name')
    # Filters available in the admin list view
    list_filter = ('course',)
    
    ordering = ('course', 'name')

# Registering models with their respective custom admin configurations
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(CourseMaterial, CourseMaterialAdmin)
