# dasha_calculator/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from datetime import datetime
import json
from .models import DashaCalculation

class DashaCalculatorView(TemplateView):
    template_name = 'dasha_calculator/index.html'

@csrf_exempt
@require_http_methods(["POST"])
def calculate_dasha(request):
    try:
        data = json.loads(request.body)
        birth_date_str = data.get('birth_date')
        
        if not birth_date_str:
            return JsonResponse({
                'success': False,
                'error': '生年月日が必要です'
            })
        
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        
        # DashaCalculationインスタンスを作成（保存はオプション）
        calculator = DashaCalculation(birth_date=birth_date)
        periods = calculator.get_dasha_periods()
        
        # 現在の日付を取得
        today = datetime.now().date()
        
        # 結果をJSONに変換（最初の30期間のみ）
        result_data = []
        for i, period in enumerate(periods[:30]):
            # 現在の期間かどうかをチェック
            is_current_period = period['start_date'] <= today <= period['end_date']
            
            antara_data = []
            for antara in period['antara_dashas']:
                is_current_antara = antara['start_date'] <= today <= antara['end_date']
                antara_data.append({
                    'number': antara['number'],
                    'start_date': antara['start_date'].strftime('%Y-%m-%d'),
                    'end_date': antara['end_date'].strftime('%Y-%m-%d'),
                    'days': antara['days'],
                    'start_age': antara['start_age'],
                    'end_age': antara['end_age'],
                    'is_current': is_current_antara
                })
            
            result_data.append({
                'maha_dasha': period['maha_dasha'],
                'start_date': period['start_date'].strftime('%Y-%m-%d'),
                'end_date': period['end_date'].strftime('%Y-%m-%d'),
                'years': period['years'],
                'start_age': period['start_age'],
                'end_age': period['end_age'],
                'antara_dashas': antara_data,
                'is_current': is_current_period
            })
        
        return JsonResponse({
            'success': True,
            'start_number': calculator.start_number,
            'periods': result_data
        })
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': '日付の形式が正しくありません'
        })
    except Exception as e:
        print("Error occurred:", str(e))  # デバッグ用
        import traceback
        traceback.print_exc()  # 詳細なエラー情報
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        })