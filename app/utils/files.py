"""
シンプルなファイルとディレクトリの管理ユーティリティ
"""

import datetime
from enum import Enum
from pathlib import Path

import pandas as pd

from app.utils import dates


# ========================================
# CONSTANTS
# ========================================
TEMP_DIR = "temp"
OUTPUTS_DIR = "outputs"
FINS_TARGETS_FILE = "fins_targets.csv"
LISTED_INFO_FILE = "listed_info.csv"


# ========================================
# ENUM
# ========================================
class DataType(Enum):
    """データタイプのENUM"""

    FINS = "fins"
    IMAGES = "images"
    LISTED_INFO = "listed_info"
    QUOTES = "quotes"


# ========================================
# CLASS
# ========================================
class FileManager:
    """シンプルなファイル管理クラス

    構造:
    data/
    ├── outputs/            # 出力データ(削除禁止)
    │   ├── 251006/
    │   └── 251007/
    └── temp/               # 一時データ(削除対象)
        ├── 251006/
        │   ├── 01234/
        │   │   ├── 01234_251006_fins.csv
        │   │   └── 01234_251006_quotes.csv
        │   ├── fins_targets.csv
        │   └── listed_info.csv
        └── 251007/
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.today = dates.get_current_jst_date()

    def get_date_string(self, date: datetime.date | None = None) -> str:
        """日付を文字列で取得(ISO形式: 2025-10-06)"""
        target_date = date or self.today
        return dates.format_date(target_date)

    def get_date_string_short(self, date: datetime.date | None = None) -> str:
        """日付を短縮形式で取得(YYMMDD形式: 251006)"""
        target_date = date or self.today
        return dates.format_date(target_date, format_type=dates.DateFormat.YYMMDD)

    def get_stock_data_path(
        self,
        normalized_code: str,
        data_type: str,
        date: datetime.date | None = None,
    ) -> Path:
        """銘柄コード別のデータファイルパスを取得

        Args:
            normalized_code: 正規化済み証券コード（5桁）
            data_type: データタイプ（"fins" or "quotes"）
            date: 日付（省略時は今日）

        Returns:
            Path: データファイルのパス
        """
        date_short = self.get_date_string_short(date)
        return (
            self.base_dir
            / TEMP_DIR
            / date_short
            / normalized_code
            / f"{normalized_code}_{date_short}_{data_type}.csv"
        )

    def get_fins_targets_path(self, date: datetime.date | None = None) -> Path:
        """対象企業の統合財務データファイルのパスを取得"""
        date_short = self.get_date_string_short(date)
        return self.base_dir / TEMP_DIR / date_short / FINS_TARGETS_FILE

    def get_listed_info_path(self, date: datetime.date | None = None) -> Path:
        """上場企業情報ファイルのパスを取得"""
        date_short = self.get_date_string_short(date)
        return self.base_dir / TEMP_DIR / date_short / LISTED_INFO_FILE

    def ensure_directory_exists(self, path: Path) -> None:
        """ディレクトリが存在しない場合は作成"""
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def save_report(
        self,
        content: str | bytes,
        filename: str,
        date: datetime.date | None = None,
    ) -> Path:
        """レポートファイルを保存(長期保存)

        Args:
            content: ファイル内容
            filename: ファイル名(拡張子込み)
            date: 日付(省略時は今日)

        Returns:
            Path: 保存されたファイルのパス
        """
        date_short = self.get_date_string_short(date)
        file_path = self.base_dir / OUTPUTS_DIR / date_short / filename

        self.ensure_directory_exists(file_path.parent)

        if isinstance(content, str):
            file_path.write_text(content, encoding="utf-8")
        else:
            file_path.write_bytes(content)

        return file_path

    def save_data(
        self,
        df: pd.DataFrame,
        filename: str,
        data_type: DataType,
        date: datetime.date | None = None,
    ) -> Path:
        """データファイルを保存(一時保存)

        Args:
            df: データフレーム
            filename: ファイル名(拡張子込み)
            data_type: データタイプ
            date: 日付(省略時は今日)

        Returns:
            Path: 保存されたファイルのパス
        """
        date_short = self.get_date_string_short(date)
        file_path = self.base_dir / TEMP_DIR / date_short / data_type.value / filename

        self.ensure_directory_exists(file_path.parent)
        df.to_csv(file_path, index=False)

        return file_path
