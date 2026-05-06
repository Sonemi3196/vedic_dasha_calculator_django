# dasha_calculator/urls.py
from django.urls import path
from . import views

app_name = 'dasha_calculator'

urlpatterns = [
    path('', views.integrated_view, name='index'),
    path('calculate/', views.calculate_integrated, name='calculate'),
    path('compare/', views.compare_dasha_view, name='compare'),
    path('compare/calculate/', views.calculate_comparison, name='calculate_comparison'),
    path('prashna/', views.prashna_view, name='prashna'),
    path('dice/', views.dice_view, name='dice'),
    
    # 認証
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # 保存機能
    path('saved/', views.saved_list, name='saved_list'),
    path('saved/add/', views.save_person, name='save_person'),
    path('saved/<int:pk>/edit/', views.edit_person, name='edit_person'),
    path('saved/<int:pk>/delete/', views.delete_person, name='delete_person'),
    path('saved/<int:pk>/load/', views.load_person, name='load_person'),

    path('login/api/', views.login_api, name='login_api'),
    path('register/api/', views.register_api, name='register_api'),
]