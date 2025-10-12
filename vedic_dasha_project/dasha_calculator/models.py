# dasha_calculator/models.py
from django.db import models
from datetime import datetime, timedelta
import math

class DashaCalculation(models.Model):
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dasha calculation for {self.birth_date}"
    
    @property
    def start_number(self):
        """生年月日から開始番号を計算"""
        day = self.birth_date.day
        while day > 9:
            day = sum(int(digit) for digit in str(day))
        return day
    
    def calculate_age(self, target_date):
        """指定日時点の年齢を計算"""
        return math.floor((target_date - self.birth_date).days / 365.25)
    
    def get_dasha_periods(self, max_periods=150):
        """ダーシャ期間を計算（アンタラダシャ累積方式）"""
        results = []
        current_date = self.birth_date + timedelta(days=1)
        maha_dasha_number = self.start_number
        
        for period in range(max_periods):
            maha_dasha_years = maha_dasha_number
            maha_dasha_start_date = current_date
            
            # アンタラダシャを先に計算
            antara_dashas = []
            antara_number = maha_dasha_number
            
            # 1年 = 365.25日とした合計日数
            total_year_days = maha_dasha_years * 365.25
            
            # 各アンタラダシャの割合（1+2+3+...+9=45）
            total_ratio = 45
            
            antara_start_date = maha_dasha_start_date 
            maha_total_days = 0  # アンタラダシャの累積日数
            
            for i in range(9):
                # 各アンタラダシャの日数 = 全体 × (番号/45)
                antara_days = round(total_year_days * antara_number / total_ratio)
                maha_total_days += antara_days
                
                antara_end_date = antara_start_date + timedelta(days=antara_days-1)
                
                # 表示用：最初の期間の最初のアンタラダシャのみ誕生日を表示
                display_antara_start = self.birth_date if (period == 0 and i == 0) else antara_start_date
                
                antara_dashas.append({
                    'number': antara_number,
                    'start_date': display_antara_start,  # 表示用
                    'end_date': antara_end_date,
                    'days': antara_days,
                    'start_age': self.calculate_age(display_antara_start),
                    'end_age': self.calculate_age(antara_end_date)
                })
                
                antara_start_date = antara_end_date + timedelta(days=1)
                antara_number = 1 if antara_number == 9 else antara_number + 1
            
            # マハーダシャの終了日はアンタラダシャの累積
            maha_dasha_end_date = antara_dashas[-1]['end_date']
            
            # 表示用：最初の期間だけ誕生日を表示
            display_start_date = self.birth_date if period == 0 else maha_dasha_start_date
            
            results.append({
                'maha_dasha': maha_dasha_number,
                'start_date': display_start_date,  # 表示用
                'end_date': maha_dasha_end_date,
                'years': maha_dasha_years,
                'total_days': maha_total_days,
                'start_age': self.calculate_age(display_start_date),
                'end_age': self.calculate_age(maha_dasha_end_date),
                'antara_dashas': antara_dashas
            })
            
            # 次のマハーダシャは前の終了日の翌日から
            current_date = maha_dasha_end_date + timedelta(days=1)
            maha_dasha_number = 1 if maha_dasha_number == 9 else maha_dasha_number + 1
        
        return results