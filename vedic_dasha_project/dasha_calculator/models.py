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
    
    def get_dasha_periods(self, max_periods=54):
        """ダーシャ期間を計算"""
        results = []
        current_date = self.birth_date
        maha_dasha_number = self.start_number
        
        for period in range(max_periods):
            maha_dasha_years = maha_dasha_number
            maha_dasha_start_date = current_date
            
            # 1年を365日固定で計算
            maha_dasha_days = maha_dasha_years * 365
            maha_dasha_end_date = maha_dasha_start_date + timedelta(days=maha_dasha_days)
            
            # アンタラダシャを計算
            antara_dashas = []
            antara_current_date = maha_dasha_start_date
            antara_number = maha_dasha_number
            
            # マハーダシャ期間を45で割った基本単位
            base_unit = maha_dasha_days / 45
            remaining_days = maha_dasha_days
            
            for i in range(9):
                if i == 8:  # 最後のアンタラダシャは残り日数をすべて使用
                    antara_days = remaining_days
                else:
                    antara_days = round(base_unit * antara_number)
                    remaining_days -= antara_days
                
                antara_start_date = antara_current_date
                antara_end_date = antara_current_date + timedelta(days=antara_days)
                
                antara_dashas.append({
                    'number': antara_number,
                    'start_date': antara_start_date,
                    'end_date': antara_end_date,
                    'days': int(antara_days),
                    'start_age': self.calculate_age(antara_start_date),
                    'end_age': self.calculate_age(antara_end_date)
                })
                
                antara_current_date = antara_end_date
                antara_number = 1 if antara_number == 9 else antara_number + 1
            
            results.append({
                'maha_dasha': maha_dasha_number,
                'start_date': maha_dasha_start_date,
                'end_date': maha_dasha_end_date,
                'years': maha_dasha_years,
                'start_age': self.calculate_age(maha_dasha_start_date),
                'end_age': self.calculate_age(maha_dasha_end_date),
                'antara_dashas': antara_dashas
            })
            
            # 次のマハーダシャ開始日は前の終了日の翌日
            current_date = maha_dasha_end_date + timedelta(days=1)
            maha_dasha_number = 1 if maha_dasha_number == 9 else maha_dasha_number + 1
        
        return results