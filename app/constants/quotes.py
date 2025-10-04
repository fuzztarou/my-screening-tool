"""
株価データ関連定数

J-Quants API から取得する株価データの処理に使用する定数を定義します。
"""

# 株価データの必須カラム
QUOTES_COLUMNS_TO_EXTRACT = [
    "Date",
    "Code",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "TurnoverValue",
    "AdjustmentFactor",
    "AdjustmentOpen",
    "AdjustmentHigh",
    "AdjustmentLow",
    "AdjustmentClose",
    "AdjustmentVolume",
]

# 株価データの数値変換対象カラム
# https://jpx.gitbook.io/j-quants-ja/api-reference/daily_quotes
QUOTES_COLUMNS_TO_NUMERIC = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "TurnoverValue",
    "AdjustmentFactor",
    "AdjustmentOpen",
    "AdjustmentHigh",
    "AdjustmentLow",
    "AdjustmentClose",
    "AdjustmentVolume",
]
