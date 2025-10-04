"""
日付関連のユーティリティ

日付の操作、フォーマット、タイムゾーン変換などの機能を提供します。
"""

import datetime
from dataclasses import dataclass
from enum import Enum


class DateFormat(Enum):
    """日付フォーマット列挙型"""

    ISO = "iso"  # YYYY-MM-DD
    YYYYMMDD = "yyyymmdd"  # YYYYMMDD
    YYMMDD = "yymmdd"  # YYMMDD (2桁年)


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


def format_date(
    date: datetime.date | None = None, format_type: DateFormat = DateFormat.ISO
) -> str:
    """日付を文字列で取得

    Args:
        date: 日付(省略時は今日)
        format_type: 出力形式(DateFormat.ISO: YYYY-MM-DD, DateFormat.YYYYMMDD: YYYYMMDD, DateFormat.YYMMDD: YYMMDD)

    Returns:
        str: 指定された形式の日付文字列
    """
    target_date = date or get_current_jst_date()

    if format_type == DateFormat.ISO:
        return target_date.strftime("%Y-%m-%d")
    if format_type == DateFormat.YYYYMMDD:
        return target_date.strftime("%Y%m%d")
    if format_type == DateFormat.YYMMDD:
        return target_date.strftime("%y%m%d")

    msg = f"Unsupported format_type: {format_type}"
    raise ValueError(msg)


def get_date_years_ago(years: int) -> datetime.date:
    """現在から指定した年数前の日付を取得

    Args:
        years: 何年前か

    Returns:
        datetime.date: 指定した年数前の日付
    """
    current_date = get_current_jst_date()
    return datetime.date(
        current_date.year - years, current_date.month, current_date.day
    )


def format_date_years_ago(years: int, format_type: DateFormat = DateFormat.ISO) -> str:
    """現在から指定した年数前の日付を文字列で取得

    Args:
        years: 何年前か
        format_type: 出力形式(DateFormat.ISO: YYYY-MM-DD, DateFormat.YYYYMMDD: YYYYMMDD)

    Returns:
        str: 指定された形式の日付文字列
    """
    return format_date(get_date_years_ago(years), format_type)
