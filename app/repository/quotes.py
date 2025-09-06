"""
株価データハンドラー

複数の証券コードの株価データを取得し、CSVファイルとして保存するサービスを提供します。
将来的には株価データの分析機能も提供予定です。
"""

import logging
from pathlib import Path

import jquantsapi
import pandas as pd

from app.client.jq import create_client
from app.utils import dates
from app.utils.files import FileManager
from app.utils.stock_code import normalize_stock_codes
from config.config import config

logger = logging.getLogger(__name__)

# 株価データの数値変換用
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


class DailyQuotesDataHandler:
    """株価データ取得・保存・分析ハンドラークラス"""

    def __init__(
        self,
        client: jquantsapi.Client | None = None,
        file_manager: FileManager | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> None:
        """
        初期化

        Args:
            client: J-Quants APIクライアント(省略時は新規作成)
            file_manager: ファイル管理クラス(省略時は新規作成)
        """
        self.client = client or create_client()
        self.file_manager = file_manager or FileManager()

        self.date_from = date_from or dates.format_date_years_ago(
            config.DATA_YEARS_AGO, format_type=dates.DateFormat.YYYYMMDD
        )

        self.date_to = date_to or dates.format_date(
            dates.get_current_jst_date(), format_type=dates.DateFormat.YYYYMMDD
        )

    def fetch_and_save_daily_quotes(self, stock_codes: list[str]) -> list[str]:
        """
        複数の証券コードの株価データを取得・保存

        Args:
            stock_codes: 証券コードのリスト

        Returns:
            list[str]: 正規化された企業コードのリスト（重複なし）
        """
        existing_count = 0
        new_count = 0

        try:
            # 証券コードのリストを一括で5桁に正規化
            normalized_codes = normalize_stock_codes(stock_codes)
        except ValueError as e:
            logger.error("証券コードの正規化に失敗しました: %s", e)
            return []

        for i, normalized_code in enumerate(normalized_codes):
            try:
                # 正規化されたコードでファイル存在チェック
                if self._csv_exists(normalized_code):
                    existing_count += 1
                    continue

                # APIからデータ取得（元のコードを使用）
                df_quotes = self._fetch_daily_quotes(stock_codes[i])

                # CSV保存（正規化されたコードを使用）
                self._save_to_csv(df_quotes, normalized_code)
                new_count += 1

            except Exception:
                logger.exception(
                    "証券コード %s の株価データ取得・保存に失敗しました",
                    stock_codes[i],
                )

        # 最終結果をログで出力
        logger.info("既存CSV: %d個, 新規CSV: %d個", existing_count, new_count)

        # 重複を削除して返却
        return list(set(normalized_codes))

    def _csv_exists(self, stock_code: str) -> bool:
        """指定した証券コードのCSVファイルが存在するかチェック"""
        date_str = self.file_manager.get_date_string()
        # 日付を YYMMDD 形式で取得
        date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
        # 5桁のコードでチェック
        csv_path = (
            self.file_manager.base_dir
            / "temporary"
            / date_str
            / stock_code
            / f"{stock_code}_{date_short}_quotes.csv"
        )
        return bool(csv_path.exists())

    def _fetch_daily_quotes(self, stock_code: str) -> pd.DataFrame:
        """APIから株価データを取得"""
        df = self.client.get_prices_daily_quotes(
            code=stock_code, from_yyyymmdd=self.date_from, to_yyyymmdd=self.date_to
        )
        return pd.DataFrame(df)

    def _save_to_csv(self, df: pd.DataFrame, stock_code: str) -> Path:
        """DataFrameをCSVファイルとして保存（5桁のAPIコードを使用）"""
        date_str = self.file_manager.get_date_string()
        # 5桁のAPIコードでディレクトリとファイル名を作成
        code_dir = self.file_manager.base_dir / "temporary" / date_str / stock_code
        self.file_manager.ensure_directory_exists(code_dir)

        # 日付を YYMMDD 形式で取得
        date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
        file_path = code_dir / f"{stock_code}_{date_short}_quotes.csv"
        df.to_csv(file_path, index=False)
        logger.info(
            "株価データを保存しました: %s (APIコード: %s)", file_path, stock_code
        )
        return file_path
