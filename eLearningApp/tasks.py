from celery import shared_task
from django.core.mail import send_mail
from .models import CustomUser, Course

# Task to send an email notification to the teacher when a student enrolls in a course
@shared_task
def send_enrollment_notification(course_id, student_id):
    # Retrieve the course and student objects based on their IDs
    course = Course.objects.get(id=course_id)
    student = CustomUser.objects.get(id=student_id)
    
    
    subject = 'New Enrollment'
    message = f'{student.full_name} has enrolled in your course: {course.title}.'
    
    # The recipient of the email is the course instructor
    recipient_list = [course.instructor.email]
    
    # Send the email
    send_mail(subject, message, 'admin@elearning.com', recipient_list)

# Task to send an email notification to all students when new material is added to a course
@shared_task
def send_material_notification(course_id):
    # Retrieve the course object based on its ID
    course = Course.objects.get(id=course_id)
    
    # Get all students enrolled in the course
    students = course.enrollments.all()
    
    # Define the email subject and message
    subject = 'New Course Material'
    message = f'New material has been added to your course: {course.title}.'
    
    # Create a list of email addresses for all enrolled students
    recipient_list = [student.student.email for student in students]
    
    # Send the email to all students
    send_mail(subject, message, 'admin@elearning.com', recipient_list)
