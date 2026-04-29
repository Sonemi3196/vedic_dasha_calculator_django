from django.urls import path
from . import views

app_name = 'dasha_calculator'

urlpatterns = [
    path('', views.integrated_view, name='index'),
    path('calculate/', views.calculate_integrated, name='calculate'),
    path('compare/', views.compare_dasha_view, name='compare'),
    path('compare/calculate/', views.calculate_comparison, name='calculate_comparison'),
    path('prashna/', views.prashna_view, name='prashna'),  # 追加
    path('dice/', views.dice_view, name='dice'),  # 追加
]