from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Initialize the default router
router = DefaultRouter()

# Register the CustomUserViewSet with the router
router.register(r'users', views.CustomUserViewSet, basename='users')

# Define the URL patterns for the API
urlpatterns = [
   
    path('', include(router.urls)),
]
