# dasha_calculator/urls.py
from django.urls import path
from . import views

app_name = 'dasha_calculator'

urlpatterns = [
    path('', views.DashaCalculatorView.as_view(), name='index'),
    path('calculate/', views.calculate_dasha, name='calculate'),  # 既に末尾にスラッシュがある
]