# dasha_calculator/urls.py
from django.urls import path
from . import views

app_name = 'dasha_calculator'

urlpatterns = [
    path('', views.DashaCalculatorView.as_view(), name='index'),
    path('calculate/', views.calculate_dasha, name='calculate'),  # 既に末尾にスラッシュがある
    # dasha_calculator/urls.py に追加
    path('compare/', views.compare_dasha_view, name='compare'),
    path('calculate_comparison/', views.calculate_comparison, name='calculate_comparison'),
]