"""
日付関連のユーティリティ

日付の操作、フォーマット、タイムゾーン変換などの機能を提供します。
"""

import datetime
from dataclasses import dataclass


# ========================================
# CONSTANTS
# ========================================
@dataclass(frozen=True)
class TimeConstants:
    """時間関連の定数クラス"""

    T_DELTA: datetime.timedelta = datetime.timedelta(hours=9)
    JST: datetime.timezone = datetime.timezone(datetime.timedelta(hours=9), "JST")


# ========================================
# FUNCTIONS
# ========================================
def get_current_jst_date() -> datetime.date:
    """現在の日本時間の日付を取得"""
    return datetime.datetime.now(TimeConstants.JST).date()


def format_date(date: datetime.date | None = None) -> str:
    """日付を文字列で取得(ISO形式: 2025-10-06)

    Args:
        date: 日付(省略時は今日)

    Returns:
        str: ISO形式の日付文字列(YYYY-MM-DD)
    """
    target_date = date or get_current_jst_date()
    return target_date.strftime("%Y-%m-%d")
