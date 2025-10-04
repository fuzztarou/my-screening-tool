"""
株価データ型定義

株価データ（df_quotes）の型定義とバリデーション機能を提供します。
"""

import logging
from typing import List, Optional

import pandas as pd

from app.constants import QUOTES_COLUMNS_TO_EXTRACT, QUOTES_COLUMNS_TO_NUMERIC

logger = logging.getLogger(__name__)


class RawQuotesData:
    """
    株価データフレームのラッパークラス

    DataFrameに対して以下の機能を提供します：
    - 必要なカラムの存在確認
    - 数値カラムの型変換
    - 型安全なアクセス
    """

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: 株価データを含むDataFrame
        """
        self._df = df.copy()

    @property
    def df(self) -> pd.DataFrame:
        """内部のDataFrameへの読み取り専用アクセス"""
        return self._df

    @classmethod
    def from_csv(cls, file_path: str) -> "RawQuotesData":
        """
        CSVファイルから株価データを読み込み

        Args:
            file_path: CSVファイルのパス

        Returns:
            RawQuotesDataインスタンス
        """
        df = pd.read_csv(file_path)
        instance = cls(df)
        instance.validate_columns()
        return instance.convert_numeric_columns()

    def validate_columns(self, required_columns: Optional[List[str]] = None) -> bool:
        """
        必要なカラムが全て存在するかを確認

        Args:
            required_columns: 確認するカラムのリスト。Noneの場合はQUOTES_COLUMNS_TO_EXTRACTを使用

        Returns:
            全てのカラムが存在する場合はTrue

        Raises:
            ValueError: 欠けているカラムがある場合
        """
        if required_columns is None:
            required_columns = QUOTES_COLUMNS_TO_EXTRACT

        existing_columns = set(self._df.columns)
        required_columns_set = set(required_columns)
        missing_columns = required_columns_set - existing_columns

        if missing_columns:
            error_msg = f"必要なカラムが不足しています: {sorted(missing_columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug("カラム検証成功: 全ての必要なカラムが存在します")
        return True

    def convert_numeric_columns(
        self, columns: Optional[List[str]] = None
    ) -> "RawQuotesData":
        """
        指定されたカラムを数値型に変換

        Args:
            columns: 変換するカラムのリスト。Noneの場合はQUOTES_COLUMNS_TO_NUMERICを使用

        Returns:
            変換後の新しいRawQuotesDataインスタンス
        """
        if columns is None:
            columns = QUOTES_COLUMNS_TO_NUMERIC

        # 存在するカラムのみを変換対象とする
        existing_columns = set(self._df.columns)
        columns_to_convert = [col for col in columns if col in existing_columns]

        if len(columns_to_convert) != len(columns):
            missing = set(columns) - existing_columns
            logger.warning(
                "一部のカラムが存在しないためスキップされます: %s", sorted(missing)
            )

        # 数値変換実行
        df_converted = self._df.copy()
        df_converted[columns_to_convert] = df_converted[columns_to_convert].apply(
            pd.to_numeric, errors="coerce"
        )

        logger.debug("%d個のカラムを数値型に変換しました", len(columns_to_convert))
        return RawQuotesData(df_converted)
