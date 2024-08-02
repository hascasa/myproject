from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment, CourseMaterial
from .tasks import send_enrollment_notification, send_material_notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Signal receiver to notify the teacher when a student enrolls in their course
@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance, created, **kwargs):
    if created:  # Check if a new enrollment instance was created
        # Call the Celery task to send the enrollment notification
        send_enrollment_notification.delay(instance.course.id, instance.student.id)

        # Notify the teacher in real-time using Django Channels
        message = f"{instance.student.full_name} has enrolled in your course: {instance.course.title}."
        group_name = f'notifications_{instance.course.instructor.username}'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'user_notification',  # Specify the type of message handler
                'notification_type': 'enrollment',  # Type of notification
                'message': message  # The notification message
            }
        )

# Signal receiver to notify students when new course material is added
@receiver(post_save, sender=CourseMaterial)
def notify_students_on_new_material(sender, instance, created, **kwargs):
    if created:  # Check if a new course material instance was created
        # Call the Celery task to send the new material notification
        send_material_notification.delay(instance.course.id)

        # Notify each enrolled student in real-time using Django Channels
        enrolled_students = instance.course.enrollments.all()
        channel_layer = get_channel_layer()
        for enrollment in enrolled_students:
            group_name = f'notifications_{enrollment.student.username}'
            message = f"New material added to your course: {instance.course.title}."
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'user_notification',  # Specify the type of message handler
                    'notification_type': 'new_material',  # Type of notification
                    'message': message  # The notification message
                }
            )
