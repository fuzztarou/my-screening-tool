## データ取得先
[J-Quants API](https://jpx-jquants.com/#jquants-api)

## API クライアント
[jquants-api-client-python](https://github.com/J-Quants/jquants-api-client-python)

## 認証情報
- `jquants-api.toml` に設定しておく
- [参照](https://github.com/J-Quants/jquants-api-client-python?tab=readme-ov-file#%E8%A8%AD%E5%AE%9A)

## 出力データのディレクトリ構成

```
data/
├── reports/            # 長期保存（削除禁止）
│   ├── 2025-10-06/
│   │   ├── 6008_report.pdf
│   │   ├── screened-01_report.pdf
│   │   ├── screened-02_report.pdf
│   │   └── all_report.pdf
│   └── 2025-10-07/
└── temporary/          # 一時データ（削除対象）
    ├── 2025-10-06/
    │   ├── fins/
    │   │   ├── 6008_fins.csv
    │   │   ├── screened-01_fins.csv
    │   │   ├── screened-02_fins.csv
    │   │   └── all_fins.csv
    │   ├── images/
    │   │   ├── 6008_report.png
    │   │   └── 1006_report.png
    │   ├── listed_info/
    │   │   ├── 6008_listed_info.csv
    │   │   ├── screened-01_listed_info.csv
    │   │   ├── screened-02_listed_info.csv
    │   │   └── all_listed_info.csv
    │   └── quotes/
    │       └── 6008_quotes.csv
    └── 2025-10-07/
```

### 特徴
- **reports/**: 長期保存が必要なレポートファイル（削除禁止）
- **temporary/**: 一時的なデータファイル（定期削除対象）
- 日付別ディレクトリで時系列管理
- データタイプ別サブディレクトリで分類

### 使用方法
```python
from app.utils.files import FileManager, DataType

# ファイル管理クラスの初期化
manager = FileManager()

# 基本的な保存方法（拡張子込みファイル名）
manager.save_data(df, "6008_fins.csv", DataType.FINS)
manager.save_report(content, "6008_report.pdf")

# 便利メソッド（拡張子自動付与）
manager.save_csv(df, "sample_data", DataType.FINS)
manager.save_pdf(pdf_content, "analysis_report")
manager.save_png(image_content, "chart")

# 銘柄データ保存
manager.save_by_stock_code(df, "6008", DataType.FINS)

# スクリーニング結果保存
manager.save_screening_result(df, "01", DataType.FINS)

```

### 主要メソッド
- **基本保存**: `save_data()`, `save_report()`
- **便利メソッド**: `save_csv()`, `save_pdf()`, `save_png()`
- **特定用途**: `save_by_stock_code()`, `save_screening_result()`
- **日付設定**: `set_date()`

### 特徴
- ディレクトリは保存時に自動作成
- ISO形式の日付（2025-10-06）を使用
- 拡張子は指定可能、便利メソッドで自動付与も可能
