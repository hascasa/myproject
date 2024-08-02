from django.contrib.auth import login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, LoginForm, CourseForm, FeedbackForm, CourseMaterialForm, StatusForm, SearchForm, CustomUserUpdateForm, CourseUpdateForm
from .models import Course, Enrollment, Feedback, CourseMaterial, Status, CustomUser
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CustomUserSerializer
from django.http import HttpResponseForbidden
from rest_framework.permissions import IsAdminUser
import requests
import os

# CustomUserViewSet for API
class CustomUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'request': self.request}


# Register function
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/') 
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


# Login function
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home', user.username)
        else:
            print(form.errors)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# Logout Function
def user_logout(request):
    logout(request)
    return redirect('/')


# Courses Function that only allows logged in users to view
@login_required
def courses(request):
    context = {}
    course_form = CourseForm()
    context['course_form'] = course_form

    # Checks if the user is a teacher
    if request.user.has_perm('eLearningApp.can_create_course'):
        # Post function for new course
        if request.method == 'POST':
            course_form = CourseForm(request.POST)
            if course_form.is_valid():
                new_course = course_form.save(commit=False)
                new_course.instructor = request.user
                new_course.save()
                return redirect('courses')
        # Prints out the teacher courses
        teacher_courses = Course.objects.filter(instructor=request.user)
        context['teacher_courses'] = teacher_courses

    # If the user is a student
    else:
        # Prints out the enrolled and available to enroll courses
        enrolled_courses = Course.objects.filter(enrollments__student=request.user)
        available_courses = Course.objects.exclude(enrollments__student=request.user)
        context['enrolled_courses'] = enrolled_courses
        context['available_courses'] = available_courses

    return render(request, 'courses.html', context)


# Allowing users to enter their home page by just typing /home
@login_required
def home_redirect(request):
    username = request.user.username
    return redirect('home', username=username)

# Home page for users that is logged in
# The users will be able to view other users home page based on their username
@login_required
def home(request, username):
    home_user = get_object_or_404(CustomUser, username=username)
    status_form = StatusForm()
    update_profile_form = CustomUserUpdateForm(instance=home_user)

    if request.method == 'POST':
        if 'leave_status' in request.POST and request.user.username == username:
            status_form = StatusForm(request.POST)
            if status_form.is_valid():
                status = status_form.save(commit=False)
                status.user = home_user
                status.save()
                return redirect('home', username=home_user.username)

        elif 'update_profile' in request.POST and request.user.username == username:
            old_photo = home_user.photo
            update_profile_form = CustomUserUpdateForm(request.POST, request.FILES, instance=home_user)
            if update_profile_form.is_valid():
                # If a new photo is uploaded, delete the old photo from the file system
                if 'photo' in request.FILES:
                    if old_photo and old_photo != 'default.jpg':
                        if os.path.isfile(old_photo.path):
                            os.remove(old_photo.path)
                update_profile_form.save()
                # Ensure the user does not get logged out after changing the password
                update_session_auth_hash(request, home_user)
                return redirect('home', username=home_user.username)

    if home_user.has_perm('eLearningApp.can_create_course'):
        courses = Course.objects.filter(instructor=home_user)
    else:
        courses = Course.objects.filter(enrollments__student=home_user)
    status_updates = Status.objects.filter(user=home_user).order_by('-created_at')

    context = {
        'home': home_user,
        'status_form': status_form if request.user.username == username else None,
        'update_profile_form': update_profile_form if request.user.username == username else None,
        'courses': courses,
        'status_updates': status_updates,
    }

    return render(request, 'home.html', context)


# Course Detail Function that only allows users that are logged in to view
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    # Check if the current user is the teacher of the course or a student
    if not (request.user == course.instructor or request.user.role == CustomUser.STUDENT):
        # If the user is neither the course instructor nor a student, deny access
        return HttpResponseForbidden("You are not allowed to view this page.")

    feedbacks = Feedback.objects.filter(course=course)
    feedback_form = FeedbackForm()
    upload_form = CourseMaterialForm()
    course_update_form = CourseUpdateForm(instance=course)

    # This page has 3 different post requests that are separated by the names of the button to submit
    if request.method == 'POST':
        # Leave feedback
        if 'leave_feedback' in request.POST:
            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.course = course
                feedback.student = request.user
                feedback.save()
                return redirect('course_detail', course_id=course.id)
        # Upload material
        elif 'upload_material' in request.POST and request.user.has_perm('eLearningApp.can_create_course'):
            upload_form = CourseMaterialForm(request.POST, request.FILES)
            if upload_form.is_valid():
                material = upload_form.save(commit=False)
                material.course = course
                material.save()
                return redirect('course_detail', course_id=course.id)
        # Remove student
        elif 'remove_student' in request.POST and request.user == course.instructor:
            student_id = request.POST.get('student_id')
            student_to_remove = Enrollment.objects.filter(student_id=student_id, course=course)
            if student_to_remove.exists():
                student_to_remove.delete()
                return redirect('course_detail', course_id=course.id)
        elif 'update_course_details' in request.POST and request.user == course.instructor:
            course_update_form = CourseUpdateForm(request.POST, instance=course)
            if course_update_form.is_valid():
                course_update_form.save()
                return redirect('course_detail', course_id=course.id)

    context = {
        'course': course,
        'enrolled': enrolled,
        'feedbacks': feedbacks,
        'feedback_form': feedback_form,
        'upload_form': upload_form,
        'course_update_form': course_update_form,
    }
    return render(request, 'course_detail.html', context)


# Enroll in course function
@login_required
def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.create(student=request.user, course=course)
    return redirect('course_detail', course_id=course_id)


# Enroll from course function
@login_required
def unenroll_from_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.filter(student=request.user, course=course).delete()
    return redirect('course_detail', course_id=course_id)


# Leave feedback for course function
@login_required
def leave_feedback(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.course = course
            feedback.student = request.user
            feedback.save()
            return redirect('course_detail', course_id=course_id)
    else:
        form = FeedbackForm()
    return render(request, 'leave_feedback.html', {'form': form, 'course': course})


# Delete Course Function
@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == "POST":
        course.delete()
        return redirect('courses')
    else:
        return redirect('course_detail', course_id=course.id)


# Delete course materials function
@login_required
@permission_required('eLearningApp.can_create_course', raise_exception=True)
def delete_material(request, material_id):
    material = get_object_or_404(CourseMaterial, id=material_id)
    course_id = material.course.id
    if request.method == "POST":
        file_path = material.file.path
        if os.path.isfile(file_path):
            os.remove(file_path)
        material.delete()
        return redirect('course_detail', course_id=course_id)
    return redirect('course_detail', course_id=course_id)


# Chat room function
@login_required
def room(request, room_name):
    return render(request, 'room.html', {'room_name': room_name})


# Search function that only allows teachers to view
@login_required
@permission_required('eLearningApp.can_create_course', raise_exception=True)
def user_search(request):
    search_form = SearchForm()
    search_results = []

    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            search_results = CustomUser.objects.filter(username__icontains=query)

    return render(request, 'user_search.html', {
        'search_form': search_form,
        'search_results': search_results,
    })


# Delete status function
@login_required
def delete_status(request, status_id):
    status = get_object_or_404(Status, id=status_id)

    if request.user == status.user:
        status.delete()
    
    return redirect('home', username=request.user.username)


# Delete Feedback Function
@login_required
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    course_id = feedback.course.id 

    if request.user == feedback.student or request.user.has_perm('eLearningApp.can_create_course'):
        feedback.delete()

    return redirect('course_detail', course_id=course_id)
