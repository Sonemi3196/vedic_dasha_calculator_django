# vedic_dasha_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dasha_calculator.urls')),  # これだけでOK
    path('numerology/', include('numerology_calculator.urls')), 
]