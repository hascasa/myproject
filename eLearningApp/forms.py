from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Course, Feedback, CourseMaterial, Status
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# Update User Profile Form
class CustomUserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    photo = forms.ImageField(required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="New Password (leave blank to keep current password)")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="Confirm New Password")

    class Meta:
        model = CustomUser
        fields = ('email', 'photo', 'new_password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        # Remove the clear checkbox button
        self.fields['photo'].widget = forms.FileInput()

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Ensure the new password and confirm password match
        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "The two password fields must match.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Ensure the email is unique
        if email and CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user

# Update Course Form
class CourseUpdateForm(forms.ModelForm):
    title = forms.CharField(required=True)
    description = forms.CharField(required=False)

    class Meta:
        model = Course
        fields = ('title', 'description')

# Registration form
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    full_name = forms.CharField(label='Full Name', required=True)
    photo = forms.ImageField(label='Photo', required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'role', 'photo')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('register', 'Register'))

    # Ensure only unique emails
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# Login form
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

# Course Form
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }

# Course Material Form
class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['file', 'name']
        help_texts = {
            'file': "Upload course material here. Supports images, PDFs, etc.",
            'name': "Please include a name for the uploaded material",
        }

# Feedback Form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'text': 'Your feedback',
        }

# Status Form
class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': "What's on your mind?"}),
        }

# Search Form
class SearchForm(forms.Form):
    query = forms.CharField(label='Search for users', max_length=100)
