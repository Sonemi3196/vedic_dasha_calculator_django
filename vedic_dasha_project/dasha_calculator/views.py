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
import re  # これを追加
import math  # これも追加（ある場合は不要）

try:
    from pykakasi import kakasi
    kks = kakasi()
    HAS_KAKASI = True
except ImportError:
    HAS_KAKASI = False


class DashaCalculatorView(TemplateView):
    template_name = 'dasha_calculator/index.html'

def compare_dasha_view(request):
    """ダーシャ比較ページ"""
    return render(request, 'dasha_calculator/compare.html')

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
        
        person_a_birth = datetime.strptime(data.get('person_a_birth'), '%Y-%m-%d').date()
        person_b_birth = datetime.strptime(data.get('person_b_birth'), '%Y-%m-%d').date()
        person_a_name = data.get('person_a_name', '人A')
        person_b_name = data.get('person_b_name', '人B')
        
        calc_a = DashaCalculation(birth_date=person_a_birth)
        calc_b = DashaCalculation(birth_date=person_b_birth)
        
        periods_a = calc_a.get_dasha_periods()
        periods_b = calc_b.get_dasha_periods()
        
        comparison_timeline = create_monthly_comparison(
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

def create_monthly_comparison(periods_a, periods_b, birth_a, birth_b):
    """月単位でダーシャを比較"""
    timeline = []
    
    # 開始年と終了年を決定
    start_year = min(birth_a.year, birth_b.year)
    end_year = start_year + 80
    
    for year in range(start_year, end_year):
        for month in range(1, 13):
            first_day = date(year, month, 1)
            
            # その月の1日時点でのダーシャを取得
            dasha_a = find_dasha_for_date(periods_a, first_day, birth_a)
            dasha_b = find_dasha_for_date(periods_b, first_day, birth_b)
            
            if dasha_a or dasha_b:
                timeline.append({
                    'year': year,
                    'month': month,
                    'date_str': f"{year}年{month}月",
                    'person_a_age': calculate_age_at_date(birth_a, first_day) if dasha_a else None,
                    'person_b_age': calculate_age_at_date(birth_b, first_day) if dasha_b else None,
                    'person_a_maha': dasha_a['maha_dasha'] if dasha_a else None,
                    'person_a_antara': dasha_a['current_antara'] if dasha_a else None,
                    'person_b_maha': dasha_b['maha_dasha'] if dasha_b else None,
                    'person_b_antara': dasha_b['current_antara'] if dasha_b else None,
                })
    
    return timeline

def find_dasha_for_date(periods, target_date, birth_date):
    if target_date < birth_date:
        return None
        
    for period in periods:
        if period['start_date'] <= target_date <= period['end_date']:
            current_antara = None
            for antara in period['antara_dashas']:
                if antara['start_date'] <= target_date <= antara['end_date']:
                    current_antara = antara['number']
                    break
            
            return {
                'maha_dasha': period['maha_dasha'],
                'current_antara': current_antara,
            }
    return None

def create_transition_comparison(periods_a, periods_b, birth_a, birth_b):
    """全ての切り替わりポイントで比較"""
    # 全ての切り替わり日を収集
    transition_dates = set()
    
    for period in periods_a:
        transition_dates.add(period['start_date'])
        for antara in period['antara_dashas']:
            transition_dates.add(antara['start_date'])
    
    for period in periods_b:
        transition_dates.add(period['start_date'])
        for antara in period['antara_dashas']:
            transition_dates.add(antara['start_date'])
    
    # ソート
    sorted_dates = sorted(transition_dates)
    
    timeline = []
    for target_date in sorted_dates:
        dasha_a = find_dasha_for_date(periods_a, target_date, birth_a)
        dasha_b = find_dasha_for_date(periods_b, target_date, birth_b)
        
        if dasha_a or dasha_b:
            timeline.append({
                'date': target_date,
                'date_str': target_date.strftime('%Y年%m月%d日'),
                'person_a_age': calculate_age_at_date(birth_a, target_date) if dasha_a else None,
                'person_b_age': calculate_age_at_date(birth_b, target_date) if dasha_b else None,
                'person_a_maha': dasha_a['maha_dasha'] if dasha_a else None,
                'person_a_antara': dasha_a['current_antara'] if dasha_a else None,
                'person_b_maha': dasha_b['maha_dasha'] if dasha_b else None,
                'person_b_antara': dasha_b['current_antara'] if dasha_b else None,
            })
    
    return timeline

def calculate_age_at_date(birth_date, target_date):
    if target_date < birth_date:
        return None
    return (target_date - birth_date).days // 365

def integrated_view(request):
    """統合鑑定ビュー"""
    return render(request, 'dasha_calculator/integrated.html')

def hiragana_to_romaji(text):
    """ひらがな→ローマ字変換"""
    if not HAS_KAKASI:
        return text.upper()
    result = kks.convert(text)
    romaji = ''.join([item['hepburn'].upper() for item in result])
    return re.sub(r'[^A-Z]', '', romaji)

@csrf_exempt
@require_http_methods(["POST"])
def calculate_integrated(request):
    """統合計算API"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '')
        birth_date_str = data.get('birth_date', '')
        
        if not birth_date_str:
            return JsonResponse({'success': False, 'error': '生年月日が必要です'})
        
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        
        # ダーシャ計算（既存のロジック使用）
        calc = DashaCalculation(birth_date=birth_date)
        dasha_periods = calc.get_dasha_periods()
        
        # 現在日付との比較
        today = datetime.now().date()
        dasha_result = []
        for i, period in enumerate(dasha_periods[:30]):
            is_current = period['start_date'] <= today <= period['end_date']
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
            
            dasha_result.append({
                'maha_dasha': period['maha_dasha'],
                'start_date': period['start_date'].strftime('%Y-%m-%d'),
                'end_date': period['end_date'].strftime('%Y-%m-%d'),
                'years': period['years'],
                'start_age': period['start_age'],
                'end_age': period['end_age'],
                'antara_dashas': antara_data,
                'is_current': is_current
            })
        
        # 数秘術計算（名前がある場合のみ）
        numerology_result = None
        if name.strip():
            if re.search(r'[ぁ-んァ-ヶ]', name):
                converted_name = hiragana_to_romaji(name)
            else:
                converted_name = re.sub(r'[^A-Z]', '', name.upper())
            
            numerology_result = calculate_numerology_for_name(converted_name, birth_date)
        
        return JsonResponse({
            'success': True,
            'dasha': {
                'start_number': calc.start_number,
                'periods': dasha_result
            },
            'numerology': numerology_result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})

def calculate_numerology_for_name(name, birth_date):
    """数秘術計算用の補助関数"""
    letter_to_number = {
        'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
        'B': 2, 'K': 2, 'R': 2,
        'C': 3, 'G': 3, 'L': 3, 'S': 3,
        'D': 4, 'M': 4, 'T': 4,
        'E': 5, 'H': 5, 'N': 5, 'X': 5,
        'U': 6, 'V': 6, 'W': 6,
        'O': 7, 'Z': 7,
        'F': 8, 'P': 8
    }
    
    letter_values = [{'letter': l, 'value': letter_to_number.get(l, 0)} for l in name]
    total = sum(item['value'] for item in letter_values)
    
    def reduce_to_single(num):
        steps = [num]
        while num >= 10:
            num = sum(int(d) for d in str(num))
            steps.append(num)
        return {'final': num, 'steps': steps}
    
    name_number = reduce_to_single(total)
    
    # バーギャング
    digits = re.sub(r'\D', '', birth_date.strftime('%Y%m%d'))
    bhagyank_total = sum(int(d) for d in digits)
    bhagyank = reduce_to_single(bhagyank_total)
    
    # ムーランク
    moolank = reduce_to_single(birth_date.day)
    
    # グリッド
    year = birth_date.year % 100
    all_digits = []
    all_digits.extend([int(d) for d in str(year)])
    all_digits.extend([int(d) for d in str(birth_date.month)])
    all_digits.extend([int(d) for d in str(birth_date.day)])
    all_digits.append(bhagyank['final'])
    if birth_date.day >= 10:
        all_digits.append(moolank['final'])
    
    digit_count = {}
    for digit in all_digits:
        if digit > 0:
            digit_count[digit] = digit_count.get(digit, 0) + 1
    
    grid = {}
    for i in range(1, 10):
        grid[i] = str(i) * digit_count.get(i, 0) if i in digit_count else ''
    
    return {
        'converted_name': name,
        'letter_values': letter_values,
        'total': total,
        'name_number': name_number,
        'bhagyank': bhagyank,
        'moolank': moolank,
        'grid': grid
    }