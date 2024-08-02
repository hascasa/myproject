from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.urls import reverse
from .models import CustomUser
from django.core.exceptions import ValidationError
import os

# Serializer for CustomUser model
class CustomUserSerializer(serializers.ModelSerializer):
    # Field to get the URL of the user
    url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['url', 'id', 'username', 'password', 'email', 'full_name', 'role', 'photo', 'is_active']
        # Set fields to optional to allow for partial update
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'is_active': {'read_only': True},
            'email': {'required': False},
            'full_name': {'required': False},
            'role': {'required': False},
            'photo': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserSerializer, self).__init__(*args, **kwargs)
        # If creating a new user, set all fields to required
        if not self.instance:
            self.fields['photo'].required = True
            self.fields['email'].required = True
            self.fields['password'].required = True
            self.fields['full_name'].required = True
            self.fields['role'].required = True

    # Override the create method to hash the password and set is_active to True
    def create(self, validated_data):
        if 'photo' not in validated_data:
            raise serializers.ValidationError({"photo": "This field is required."})
        # Hash the password
        validated_data['password'] = make_password(validated_data.get('password'))
        validated_data['is_active'] = True
        return super().create(validated_data)

    # Override the update method to handle password hashing and photo removal
    def update(self, instance, validated_data):
        # Hash the password if it is in the validated data
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # If a new photo is provided, remove the old one
        new_photo = validated_data.get('photo', None)
        if new_photo and instance.photo:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
        
        # If no new photo is chosen, remove the photo key from validated_data
        if 'photo' in validated_data and not validated_data['photo']:
            validated_data.pop('photo')

        return super().update(instance, validated_data)

    # Validate that the email is unique
    def validate_email(self, value):
        if self.instance and self.instance.email == value:
            return value
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    # Method to get the absolute URL of the user
    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('users-detail', args=[obj.pk]))
