from django.urls import path
from . import views

app_name = 'dasha_calculator'

urlpatterns = [
    path('', views.integrated_view, name='index'),  # 統合ビューに変更
    path('calculate/', views.calculate_integrated, name='calculate'),  # 統合計算APIに変更
    path('compare/', views.compare_dasha_view, name='compare'),
    path('compare/calculate/', views.calculate_comparison, name='calculate_comparison'),
]