"""
シンプルなファイルとディレクトリの管理ユーティリティ
"""

import datetime
from enum import Enum
from pathlib import Path

import pandas as pd

from app.utils import dates


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
    │   ├── 2025-10-06/
    │   └── 2025-10-07/
    └── temporary/          # 一時データ(削除対象)
        ├── 2025-10-06/
        │   ├── fins/
        │   ├── images/
        │   ├── listed_info/
        │   └── quotes/
        └── 2025-10-07/
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.today = dates.get_current_jst_date()

    def set_date(self, date: datetime.date) -> None:
        """作業対象の日付を設定"""
        self.today = date

    def get_date_string(self, date: datetime.date | None = None) -> str:
        """日付を文字列で取得(ISO形式: 2025-10-06)"""
        target_date = date or self.today
        return dates.format_date(target_date)

    def get_date_string_short(self, date: datetime.date | None = None) -> str:
        """日付を短縮形式で取得(YYMMDD形式: 251006)"""
        target_date = date or self.today
        return dates.format_date(target_date, format_type=dates.DateFormat.YYMMDD)

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
        date_str = self.get_date_string(date)
        file_path = self.base_dir / "outputs" / date_str / filename

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
        date_str = self.get_date_string(date)
        file_path = self.base_dir / "temporary" / date_str / data_type.value / filename

        self.ensure_directory_exists(file_path.parent)
        df.to_csv(file_path, index=False)

        return file_path

    def save_csv(
        self,
        df: pd.DataFrame,
        base_name: str,
        data_type: DataType,
        date: datetime.date | None = None,
    ) -> Path:
        """CSVファイルとして保存(拡張子自動付与)"""
        filename = f"{base_name}.csv"
        return self.save_data(df, filename, data_type, date)

    def save_pdf(
        self,
        content: bytes,
        base_name: str,
        date: datetime.date | None = None,
    ) -> Path:
        """PDFファイルとして保存(拡張子自動付与)"""
        filename = f"{base_name}.pdf"
        return self.save_report(content, filename, date)

    def save_png(
        self,
        content: bytes,
        base_name: str,
        data_type: DataType = DataType.IMAGES,
        date: datetime.date | None = None,
    ) -> Path:
        """PNGファイルとして保存(拡張子自動付与)"""
        filename = f"{base_name}.png"
        date_str = self.get_date_string(date)
        file_path = self.base_dir / "temporary" / date_str / data_type.value / filename

        self.ensure_directory_exists(file_path.parent)
        file_path.write_bytes(content)

        return file_path

    def save_by_stock_code(
        self,
        df: pd.DataFrame,
        stock_code: str,
        data_type: DataType,
        date: datetime.date | None = None,
    ) -> Path:
        """銘柄コード付きファイルとして保存"""
        filename = f"{stock_code}_{data_type.value}.csv"
        return self.save_data(df, filename, data_type, date)

    def save_screening_result(
        self,
        df: pd.DataFrame,
        screening_id: str,
        data_type: DataType,
        date: datetime.date | None = None,
    ) -> Path:
        """スクリーニング結果ファイルとして保存"""
        filename = f"screened-{screening_id}_{data_type.value}.csv"
        return self.save_data(df, filename, data_type, date)
