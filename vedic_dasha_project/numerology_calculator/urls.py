from django.urls import path
from . import views

app_name = 'numerology_calculator'

urlpatterns = [
    path('', views.numerology_view, name='index'),
    path('calculate/', views.calculate_numerology, name='calculate'),
]