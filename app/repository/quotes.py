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

    def prepare_daily_quotes_data(self, normalized_codes: list[str]) -> None:
        """
        複数の証券コードの株価データを準備

        Args:
            normalized_codes: 正規化済み証券コードのリスト
        """
        logger.info(
            "株価データの取得・保存を開始します（対象: %d銘柄）", len(normalized_codes)
        )

        existing_count = 0
        new_count = 0

        for i, normalized_code in enumerate(normalized_codes):
            try:
                # 単一証券コードのCSVファイル存在を確保
                is_new_data = self._ensure_stock_quotes_csv(normalized_code)
                if is_new_data:
                    new_count += 1
                else:
                    existing_count += 1

            except Exception:
                logger.exception(
                    "証券コード %s の株価データ取得・保存に失敗しました",
                    normalized_codes[i],
                )

        # 最終結果をログで出力
        logger.info(
            "株価データ取得完了 - 既存CSV: %d個, 新規CSV: %d個",
            existing_count,
            new_count,
        )

    def _ensure_stock_quotes_csv(self, normalized_code: str) -> bool:
        """
        単一の証券コードの株価データCSVファイルの存在を確保

        Args:
            normalized_code: 正規化済み証券コード（5桁）

        Returns:
            bool: 新規データを保存した場合True、既存データの場合False
        """
        # 正規化されたコードでファイル存在チェック
        if self._csv_exists(normalized_code):
            return False

        # APIからデータ取得
        df_quotes = self._fetch_daily_quotes(normalized_code)

        # CSV保存（正規化されたコードを使用）
        self._save_to_csv(df_quotes, normalized_code)
        return True

    def _csv_exists(self, normalized_code: str) -> bool:
        """指定した証券コードのCSVファイルが存在するかチェック"""
        date_str = self.file_manager.get_date_string()
        date_short = self.file_manager.get_date_string_short()
        # 5桁のコードでチェック
        csv_path = (
            self.file_manager.base_dir
            / "temporary"
            / date_str
            / normalized_code
            / f"{normalized_code}_{date_short}_quotes.csv"
        )
        return bool(csv_path.exists())

    def _fetch_daily_quotes(self, normalized_code: str) -> pd.DataFrame:
        """APIから株価データを取得"""
        df = self.client.get_prices_daily_quotes(
            code=normalized_code, from_yyyymmdd=self.date_from, to_yyyymmdd=self.date_to
        )
        return pd.DataFrame(df)

    def _save_to_csv(self, df: pd.DataFrame, normalized_code: str) -> Path:
        """DataFrameをCSVファイルとして保存（5桁のAPIコードを使用）"""
        date_str = self.file_manager.get_date_string()
        date_short = self.file_manager.get_date_string_short()
        # 5桁のAPIコードでディレクトリとファイル名を作成
        code_dir = self.file_manager.base_dir / "temporary" / date_str / normalized_code
        self.file_manager.ensure_directory_exists(code_dir)

        file_path = code_dir / f"{normalized_code}_{date_short}_quotes.csv"
        df.to_csv(file_path, index=False)
        logger.info(
            "株価データを保存しました: %s (APIコード: %s)", file_path, normalized_code
        )
        return file_path
