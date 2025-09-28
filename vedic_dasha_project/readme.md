# Django ヴェーダ数秘術ダーシャ計算ツール

生年月日からヴェーダ数秘術のマハーダシャとアンタラダシャの期間を自動計算するDjangoアプリケーションです。

## 機能

- Django MVCアーキテクチャを採用
- モデル、ビュー、テンプレートの分離設計
- 管理画面対応（Django Admin）
- データベース対応（オプションで計算履歴保存）
- 年齢表示機能
- 現在の期間のハイライト表示
- 120歳相当まで表示

## アーキテクチャ

### Flask vs Django 比較

| 項目 | Flask | Django |
|------|-------|---------|
| 学習コスト | 低い | 中程度 |
| 初期設定 | 簡単 | やや複雑 |
| 機能 | ミニマル | フルスタック |
| 管理画面 | なし | 自動生成 |
| ORM | 別途必要 | 内蔵 |
| セキュリティ | 手動設定 | 自動対応 |

## ディレクトリ構造

```
vedic-dasha-calculator/
├── manage.py                          # Django管理コマンド
├── requirements.txt                   # Python依存関係
├── vedic_dasha_project/              # プロジェクト設定
│   ├── __init__.py
│   ├── settings.py                    # Django設定
│   ├── urls.py                       # プロジェクトURL設定
│   └── wsgi.py                       # WSGI設定
└── dasha_calculator/                  # アプリケーション
    ├── __init__.py
    ├── models.py                      # データモデル
    ├── views.py                       # ビューロジック
    ├── urls.py                       # アプリURL設定
    ├── admin.py                      # 管理画面設定
    ├── apps.py                       # アプリ設定
    ├── migrations/                   # データベースマイグレーション
    └── templates/
        └── dasha_calculator/
            └── index.html            # HTMLテンプレート
```

## セットアップ

### 必要なもの
- Python 3.8以上

### インストール

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/vedic-dasha-calculator-django.git
cd vedic-dasha-calculator-django
```

2. 仮想環境を作成
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. データベースのマイグレーション
```bash
python manage.py makemigrations
python manage.py migrate
```

5. スーパーユーザー作成（オプション）
```bash
python manage.py createsuperuser
```

6. アプリケーションを実行
```bash
python manage.py runserver
```

7. ブラウザで http://localhost:8000 にアクセス

## 追加ファイル

### dasha_calculator/admin.py
```python
from django.contrib import admin
from .models import DashaCalculation

@admin.register(DashaCalculation)
class DashaCalculationAdmin(admin.ModelAdmin):
    list_display = ['birth_date', 'start_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['birth_date']
    readonly_fields = ['start_number']
```

### dasha_calculator/apps.py
```python
from django.apps import AppConfig

class DashaCalculatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dasha_calculator'
    verbose_name = 'ダーシャ計算'
```

## 主な特徴

### Djangoの利点
- **ORM**: データベース操作が簡単
- **管理画面**: 自動生成される管理インターface
- **セキュリティ**: CSRF保護、SQLインジェクション対策が標準
- **スケーラビリティ**: 大規模アプリに対応
- **テスト**: 統合されたテストフレームワーク

### Flask vs Django

**Flask の場合:**
- シンプルで軽量
- 小〜中規模プロジェクトに適している
- 自由度が高い
- 学習コストが低い

**Django の場合:**
- フルスタックフレームワーク
- 中〜大規模プロジェクトに適している
- 多くの機能が標準装備
- コードの一貫性が保ちやすい

## デプロイ

### Heroku
1. Procfileを作成
```
web: gunicorn vedic_dasha_project.wsgi
release: python manage.py migrate
```

2. settings.pyにHeroku設定を追加
```python
import django_heroku
django_heroku.settings(locals())
```

### Railway / Render
各プラットフォームの指示に従って、`vedic_dasha_project.wsgi:application`をエントリーポイントとしてデプロイ

## 管理画面

Django Adminを使用して計算履歴を管理できます：
- http://localhost:8000/admin にアクセス
- スーパーユーザーでログイン
- ダーシャ計算履歴の閲覧・管理

## ライセンス

MIT License

## 貢献

プルリクエストや課題報告を歓迎します。

## 注意事項

- 1年を365日固定で計算
- ヴェーダ占星術の伝統的な計算方法に基づく
- 娯楽目的での使用を想定