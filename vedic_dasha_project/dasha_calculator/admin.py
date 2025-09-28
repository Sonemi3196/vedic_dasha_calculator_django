# dasha_calculator/admin.py
from django.contrib import admin
from .models import DashaCalculation

@admin.register(DashaCalculation)
class DashaCalculationAdmin(admin.ModelAdmin):
    list_display = ['birth_date', 'start_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['birth_date']
    readonly_fields = ['start_number', 'created_at']
    
    def start_number(self, obj):
        return obj.start_number
    start_number.short_description = '開始番号'