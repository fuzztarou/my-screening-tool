"""
ファイルとディレクトリの管理ユーティリティ
"""

import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pandas as pd


# ========================================
# CONSTANTS
# ========================================
@dataclass(frozen=True)
class TimeConstants:
    """時間関連の定数クラス"""

    T_DELTA: datetime.timedelta = datetime.timedelta(hours=9)
    JST: datetime.timezone = datetime.timezone(datetime.timedelta(hours=9), "JST")


# ========================================
# ENUM
# ========================================
class SubDirectory(Enum):
    """
    サブディレクトリのENUM
    QUOTES = "quotes"
    IMAGES = "images"
    FINS = "fins"
    """

    QUOTES = "quotes"
    IMAGES = "images"
    FINS = "fins"


class FileExtension(Enum):
    """ファイル拡張子のENUM"""

    CSV = ".csv"
    JSON = ".json"
    TXT = ".txt"
    PDF = ".pdf"
    PNG = ".png"
    JPG = ".jpg"


class DateFormat(Enum):
    """
    日付フォーマットのENUM
    ISO = "%Y-%m-%d"  # 2025-06-26
    COMPACT = "%Y%m%d"  # 20250626
    SLASH = "%Y/%m/%d"  # 2025/06/26
    JAPANESE = "%Y年%m月%d日"  # 2025年06月26日
    """

    ISO = "%Y-%m-%d"  # 2025-06-26
    COMPACT = "%Y%m%d"  # 20250626
    SLASH = "%Y/%m/%d"  # 2025/06/26
    JAPANESE = "%Y年%m月%d日"  # 2025年06月26日


class BaseDirectory(Enum):
    """
    ベースディレクトリのENUM
    DATA = "data"
    OUTPUT = "output"
    TEMP = "temp"
    """

    DATA = "data"
    OUTPUT = "output"
    TEMP = "temp"


# ========================================
# CLASS
# ========================================
class FileNameBuilder:
    """日付を含むファイル名の生成クラス"""

    def __init__(self, date_format: DateFormat = DateFormat.ISO):
        self.date_format = date_format

    def build_filename(
        self, base_name: str, date: datetime.date, extension: FileExtension
    ) -> str:
        """日付を含むファイル名を生成"""
        date_str = date.strftime(self.date_format.value)
        return f"{base_name}_{date_str}{extension.value}"

    def build_directory_name(self, date: datetime.date) -> str:
        """日付ディレクトリ名を生成"""
        return date.strftime(self.date_format.value)


class DateBasedFileManager:
    """日付ベースのディレクトリとファイル管理クラス"""

    def __init__(
        self,
        base_dir: BaseDirectory = BaseDirectory.DATA,
        date_format: DateFormat = DateFormat.ISO,
    ):
        self.base_dir = base_dir
        self.filename_builder = FileNameBuilder(date_format)
        self.current_date = datetime.datetime.now(TimeConstants.JST).date()

    def set_date(self, date: datetime.date) -> None:
        """作業対象の日付を設定"""
        self.current_date = date

    def get_date_string(self) -> str:
        """設定された日付を文字列で取得"""
        return self.filename_builder.build_directory_name(self.current_date)

    def create_date_directory_structure(
        self, date: datetime.date | None = None
    ) -> Path:
        """日付ベースのディレクトリ構造を作成

        作成されるディレクトリ構造例:
        data/2025-06-26/
        ├── quotes/
        ├── images/
        └── fins/
        """
        target_date = date or self.current_date
        date_dir = self.filename_builder.build_directory_name(target_date)

        # メインディレクトリ作成
        main_path = Path(self.base_dir.value) / date_dir
        self._ensure_directory_exists(main_path)

        # サブディレクトリ作成
        for subdir in SubDirectory:
            subdir_path = Path(main_path) / subdir.value
            self._ensure_directory_exists(subdir_path)

        return main_path

    def create_file_with_date(
        self,
        base_filename: str,
        content: str,
        subdir: SubDirectory | None = None,
        extension: FileExtension = FileExtension.CSV,
        date: datetime.date | None = None,
    ) -> Path:
        """日付を含むファイル名でファイルを作成"""
        target_date = date or self.current_date

        filename = self.filename_builder.build_filename(
            base_filename, target_date, extension
        )
        file_path = self.get_file_path(filename, subdir, target_date)

        # ディレクトリが存在しない場合は作成
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # ファイル作成処理
        self._write_file(file_path, content)
        return file_path

    def get_file_path(
        self,
        filename: str,
        subdir: SubDirectory | None = None,
        date: datetime.date | None = None,
    ) -> Path:
        """完全なファイルパスを生成"""
        target_date = date or self.current_date
        date_dir = self.filename_builder.build_directory_name(target_date)

        base_path = Path(self.base_dir.value) / date_dir
        if subdir:
            return base_path / subdir.value / filename

        return base_path / filename

    def save_dataframe_with_date(
        self,
        df: pd.DataFrame,
        base_filename: str,
        subdir: SubDirectory | None = None,
        date: datetime.date | None = None,
    ) -> Path:
        """データフレームを日付付きCSVファイルとして保存"""
        target_date = date or self.current_date
        filename = self.filename_builder.build_filename(
            base_filename, target_date, FileExtension.CSV
        )
        file_path = self.get_file_path(filename, subdir, target_date)

        # ディレクトリが存在しない場合は作成
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # CSVファイルとして保存
        df.to_csv(file_path, index=False)
        return file_path

    def _ensure_directory_exists(self, path: Path | str) -> None:
        """ディレクトリが存在しない場合は作成"""
        # 文字列が渡された場合は Path オブジェクトに変換
        path_obj = Path(path) if isinstance(path, str) else path

        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)

    def _write_file(self, file_path: Path, content: str) -> None:
        """ファイルを書き込み"""
        with Path.open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
