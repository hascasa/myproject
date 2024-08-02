from django.contrib import admin
from django.urls import path, include

#  the URL patterns 
urlpatterns = [
    # Admin site URL
    path('admin/', admin.site.urls),
    
    # API URLs 
    path('api/', include('eLearningApp.api_urls')),
    
    # WebSocket URLs 
    path('ws/', include('eLearningApp.websocket_urls')),
    
    #  URLs included 
    path('', include('eLearningApp.urls')),
]
