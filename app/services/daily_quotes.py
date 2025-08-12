"""
株価データハンドラー

複数の証券コードの株価データを取得し、CSVファイルとして保存するサービスを提供します。
将来的には株価データの分析機能も提供予定です。
"""

import logging
from operator import ge
from pathlib import Path

import jquantsapi
import pandas as pd

from app.client.jq import create_client
from app.utils import dates
from app.utils.files import DataType, FileManager
from config.config import config

logger = logging.getLogger(__name__)


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

    def fetch_and_save_daily_quotes(self, stock_codes: list[str]) -> None:
        """
        複数の証券コードの株価データを取得・保存

        Args:
            stock_codes: 証券コードのリスト
        """
        existing_count = 0
        new_count = 0

        for code in stock_codes:
            try:
                if self._csv_exists(code):
                    existing_count += 1
                    continue

                # APIからデータ取得
                df_quotes = self._fetch_daily_quotes(code)

                # CSV保存
                self._save_to_csv(df_quotes, code)
                new_count += 1

            except Exception:
                logger.exception(
                    "証券コード %s の株価データ取得・保存に失敗しました",
                    code,
                )

        # 最終結果をログで出力
        logger.info("既存CSV: %d個, 新規CSV: %d個", existing_count, new_count)

    def _csv_exists(self, stock_code: str) -> bool:
        """指定した証券コードのCSVファイルが存在するかチェック"""
        date_str = self.file_manager.get_date_string()
        csv_path = (
            self.file_manager.base_dir
            / "temporary"
            / date_str
            / stock_code
            / f"{stock_code}_quotes.csv"
        )
        return bool(csv_path.exists())

    def _fetch_daily_quotes(self, stock_code: str) -> pd.DataFrame:
        """APIから株価データを取得"""
        df = self.client.get_prices_daily_quotes(
            code=stock_code, from_yyyymmdd=self.date_from, to_yyyymmdd=self.date_to
        )
        return pd.DataFrame(df)

    def _save_to_csv(self, df: pd.DataFrame, stock_code: str) -> Path:
        """DataFrameをCSVファイルとして保存"""
        date_str = self.file_manager.get_date_string()
        code_dir = self.file_manager.base_dir / "temporary" / date_str / stock_code
        self.file_manager.ensure_directory_exists(code_dir)

        file_path = code_dir / f"{stock_code}_quotes.csv"
        df.to_csv(file_path, index=False)
        logger.info("株価データを保存しました: %s", file_path)
        return file_path
