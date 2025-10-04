"""
型定義モジュール

アプリケーションで使用する型定義を提供します。
"""

from app.types.financial_data import RawFinancialData
from app.types.quotes_data import RawQuotesData

__all__ = ["RawFinancialData", "RawQuotesData"]
