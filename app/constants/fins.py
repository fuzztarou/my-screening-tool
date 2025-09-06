"""
財務データ関連定数

J-Quants API から取得する財務データの処理に使用する定数を定義します。
"""

# 財務データのフィルタリング用カラム (必要なカラム)
FINS_COLUMNS_TO_EXTRACT = [
    "DisclosedDate",
    "LocalCode",
    "TypeOfDocument",
    "NetSales",
    "OperatingProfit",
    "OrdinaryProfit",
    "Profit",
    "EarningsPerShare",
    "ForecastNetSales",
    "ForecastOperatingProfit",
    "ForecastOrdinaryProfit",
    "ForecastProfit",
    "ForecastEarningsPerShare",
    "NextYearForecastNetSales",
    "NextYearForecastOperatingProfit",
    "NextYearForecastOrdinaryProfit",
    "NextYearForecastProfit",
    "NextYearForecastEarningsPerShare",
    "TotalAssets",
    "Equity",
    "EquityToAssetRatio",
    "BookValuePerShare",
    "NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock",
    "AverageNumberOfShares",
]

# 財務データの数値変換対象カラム
FINS_COLUMNS_TO_NUMERIC = [
    "NetSales",
    "OperatingProfit",
    "OrdinaryProfit",
    "Profit",
    "EarningsPerShare",
    "ForecastNetSales",
    "ForecastOperatingProfit",
    "ForecastOrdinaryProfit",
    "ForecastProfit",
    "ForecastEarningsPerShare",
    "NextYearForecastNetSales",
    "NextYearForecastOperatingProfit",
    "NextYearForecastOrdinaryProfit",
    "NextYearForecastProfit",
    "NextYearForecastEarningsPerShare",
    "TotalAssets",
    "Equity",
    "EquityToAssetRatio",
    "BookValuePerShare",
    "NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock",  # 発行済株式数
    "AverageNumberOfShares",
]
