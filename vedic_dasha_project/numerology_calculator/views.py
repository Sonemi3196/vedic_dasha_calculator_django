from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import re
from pykakasi import kakasi

kks = kakasi()

def numerology_view(request):
    """数秘術計算ページ"""
    return render(request, 'numerology_calculator/index.html')

def hiragana_to_romaji(text):
    """ひらがなをヘボン式ローマ字に変換"""
    result = kks.convert(text)
    romaji = ''.join([item['hepburn'].upper() for item in result])
    # スペースと記号を削除
    romaji = re.sub(r'[^A-Z]', '', romaji)
    return romaji

@csrf_exempt
@require_http_methods(["POST"])
def calculate_numerology(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '')
        birth_date = data.get('birth_date', '')
        
        if not name or not birth_date:
            return JsonResponse({
                'success': False,
                'error': '名前と生年月日が必要です'
            })
        
        # ひらがなが含まれていればローマ字に変換
        if re.search(r'[ぁ-ん]', name):
            name = hiragana_to_romaji(name)
        
        # アルファベット以外を削除
        name = re.sub(r'[^A-Z]', '', name.upper())
        
        # 文字と数字の対応
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
        
        # 各文字の数値を計算
        letter_values = []
        total = 0
        for letter in name:
            value = letter_to_number.get(letter, 0)
            letter_values.append({'letter': letter, 'value': value})
            total += value
        
        # 名前番号を計算
        name_number = reduce_to_single_digit(total)
        
        # バーギャング（生年月日全体）
        bhagyank = calculate_bhagyank(birth_date)
        
        # ムーランク（生まれた日）
        moolank = calculate_moolank(birth_date)
        
        # グリッドを計算
        grid = calculate_grid(birth_date, bhagyank['final'], moolank['final'])
        
        return JsonResponse({
            'success': True,
            'converted_name': name,
            'letter_values': letter_values,
            'total': total,
            'name_number': name_number,
            'bhagyank': bhagyank,
            'moolank': moolank,
            'grid': grid
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def reduce_to_single_digit(num):
    """数字を一桁にする"""
    steps = [num]
    while num >= 10:
        num = sum(int(digit) for digit in str(num))
        steps.append(num)
    return {'final': num, 'steps': steps}

def calculate_bhagyank(date_string):
    """バーギャングを計算"""
    digits = re.sub(r'\D', '', date_string)
    total = sum(int(digit) for digit in digits)
    return reduce_to_single_digit(total)

def calculate_moolank(date_string):
    """ムーランクを計算"""
    from datetime import datetime
    date = datetime.strptime(date_string, '%Y-%m-%d')
    day = date.day
    return reduce_to_single_digit(day)

def calculate_grid(date_string, bhagyank_num, moolank_num):
    """グリッドを計算"""
    from datetime import datetime
    date = datetime.strptime(date_string, '%Y-%m-%d')
    year = date.year
    month = date.month
    day = date.day
    
    year_last_two = year % 100
    all_digits = []
    
    # 年の下2桁
    all_digits.extend([int(d) for d in str(year_last_two)])
    # 月
    all_digits.extend([int(d) for d in str(month)])
    # 日
    all_digits.extend([int(d) for d in str(day)])
    # バーギャング
    all_digits.append(bhagyank_num)
    
    # 日が2桁ならムーランクも追加
    if day >= 10:
        all_digits.append(moolank_num)
    
    # 各数字の出現回数をカウント
    digit_count = {}
    for digit in all_digits:
        if digit > 0:  # 0は除外
            digit_count[digit] = digit_count.get(digit, 0) + 1
    
    # グリッド作成
    grid = {}
    for i in range(1, 10):
        if i in digit_count:
            grid[i] = str(i) * digit_count[i]
        else:
            grid[i] = ''
    
    return grid