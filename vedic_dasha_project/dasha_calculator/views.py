# dasha_calculator/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from datetime import datetime,date
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
    
def calculate_comparison(request):
    try:
        data = json.loads(request.body)
        
        # 2人分の生年月日を取得
        person_a_birth = datetime.strptime(data.get('person_a_birth'), '%Y-%m-%d').date()
        person_b_birth = datetime.strptime(data.get('person_b_birth'), '%Y-%m-%d').date()
        person_a_name = data.get('person_a_name', '人A')
        person_b_name = data.get('person_b_name', '人B')
        
        # 各人のダーシャを計算
        calc_a = DashaCalculation(birth_date=person_a_birth)
        calc_b = DashaCalculation(birth_date=person_b_birth)
        
        periods_a = calc_a.get_dasha_periods()
        periods_b = calc_b.get_dasha_periods()
        
        # 比較用タイムラインを作成
        comparison_timeline = create_yearly_comparison(
            periods_a, periods_b, person_a_birth, person_b_birth
        )
        
        return JsonResponse({
            'success': True,
            'person_a_name': person_a_name,
            'person_b_name': person_b_name,
            'timeline': comparison_timeline
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def create_yearly_comparison(periods_a, periods_b, birth_a, birth_b):
    """年単位でダーシャを比較"""
    timeline = []
    
    # 開始年と終了年を決定
    start_year = min(birth_a.year, birth_b.year)
    end_year = start_year + 80  # 80年間表示
    
    for year in range(start_year, end_year):
        jan_1 = date(year, 1, 1)
        
        # その年の1月1日時点でのダーシャを取得
        dasha_a = find_dasha_for_date(periods_a, jan_1, birth_a)
        dasha_b = find_dasha_for_date(periods_b, jan_1, birth_b)
        
        if dasha_a or dasha_b:  # どちらかが生存期間の場合
            timeline.append({
                'year': year,
                'person_a_age': calculate_age_at_date(birth_a, jan_1) if dasha_a else None,
                'person_b_age': calculate_age_at_date(birth_b, jan_1) if dasha_b else None,
                'person_a_maha': dasha_a['maha_dasha'] if dasha_a else None,
                'person_a_antara': dasha_a['current_antara'] if dasha_a else None,
                'person_b_maha': dasha_b['maha_dasha'] if dasha_b else None,
                'person_b_antara': dasha_b['current_antara'] if dasha_b else None,
            })
    
    return timeline

def find_dasha_for_date(periods, target_date, birth_date):
    """指定日時点でのダーシャを検索"""
    if target_date < birth_date:
        return None
        
    for period in periods:
        if period['start_date'] <= target_date <= period['end_date']:
            # 現在のアンタラダーシャも検索
            current_antara = None
            for antara in period['antara_dashas']:
                if antara['start_date'] <= target_date <= antara['end_date']:
                    current_antara = antara['number']
                    break
            
            return {
                'maha_dasha': period['maha_dasha'],
                'current_antara': current_antara,
                'period_start': period['start_date'],
                'period_end': period['end_date']
            }
    
    return None

def calculate_age_at_date(birth_date, target_date):
    """指定日時点での年齢を計算"""
    if target_date < birth_date:
        return None
    return (target_date - birth_date).days // 365