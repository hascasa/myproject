from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

# Initialize the default router
router = DefaultRouter()

# Register the CustomUserViewSet with the router
router.register(r'users', views.CustomUserViewSet, basename='users')

# URL patterns for the application
urlpatterns = [
    path('register/', views.register, name='register'),  # URL for user registration
    path('logout/', views.user_logout, name='logout'),  # URL for user logout
    path('courses/', views.courses, name='courses'),  # URL for viewing courses
    path('home/', views.home_redirect, name='home_redirect'),  # URL for redirecting to home based on username
    path('home/<str:username>/', views.home, name='home'),  # URL for viewing user's home page
    path('delete_status/<int:status_id>/', views.delete_status, name='delete_status'),  # URL for deleting a status
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),  # URL for viewing course details
    path('courses/<int:course_id>/enroll/', views.enroll_in_course, name='enroll_in_course'),  # URL for enrolling in a course
    path('courses/<int:course_id>/unenroll/', views.unenroll_from_course, name='unenroll_from_course'),  # URL for unenrolling from a course
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),  # URL for deleting a course
    path('courses/<int:course_id>/feedback/', views.leave_feedback, name='leave_feedback'),  # URL for leaving feedback on a course
    path('materials/delete/<int:material_id>/', views.delete_material, name='delete_material'),  # URL for deleting course material
    path('delete_feedback/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),  # URL for deleting feedback
    path('chat/<str:room_name>/', views.room, name='room'),  # URL for accessing chat rooms
    path('search/', views.user_search, name='user_search'),  # URL for searching users
    path('', views.user_login, name='login'),  # Default URL for user login

    # API Path
    path('api/', include(router.urls)),  # URL for API endpoints
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
