from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.validators import MinLengthValidator

# Custom user manager to handle the creation of users and superusers
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, email, password, **extra_fields)

# Custom user model
class CustomUser(AbstractUser, PermissionsMixin):
    STUDENT = 'student'
    TEACHER = 'teacher'

    ROLE_CHOICES = [
        (STUDENT, _('Student')),
        (TEACHER, _('Teacher')),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=150, default='Please Update')
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="elearning_users",
        related_query_name="elearning_user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="elearning_user_permissions",
        related_query_name="elearning_user_permission",
    )

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        # Assign the teacher the permission to create courses
        if is_new and self.role == CustomUser.TEACHER:
            assign_teacher_permissions(self)

# Assign the permission to teachers function
def assign_teacher_permissions(user):
    course_content_type = ContentType.objects.get_for_model(Course)
    permission, _ = Permission.objects.get_or_create(codename='can_create_course',
                                                     name='Can create course',
                                                     content_type=course_content_type)
    user.user_permissions.add(permission)

# Course model
class Course(models.Model):
    title = models.CharField(max_length=200, validators=[MinLengthValidator(10)])
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses'
    )

    class Meta:
        permissions = [
            ("can_create_course", "Can create course"),
        ]

    def __str__(self):
        return self.title

# Course Material model
class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, related_name='materials', on_delete=models.CASCADE)
    file = models.FileField(upload_to='course_materials/')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name or f"Material for {self.course.title}"

# Enrollment model
class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.course.title}"

# Feedback model
class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="feedbacks")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.student} on {self.course}"

# Status model
class Status(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="statuses")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"
