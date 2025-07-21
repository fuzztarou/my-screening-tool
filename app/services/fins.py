"""
財務データハンドラー

複数の証券コードの財務データを取得し、CSVファイルとして保存するサービスを提供します。
将来的には財務データの分析機能も提供予定です。
"""

import logging
from pathlib import Path
from typing import Optional

import jquantsapi
import pandas as pd

from app.client.jq import create_client
from app.utils.files import DataType, FileManager

logger = logging.getLogger(__name__)


class FinsDataHandler:
    """財務データ取得・保存・分析ハンドラークラス"""

    def __init__(
        self,
        client: jquantsapi.Client | None = None,
        file_manager: FileManager | None = None,
    ) -> None:
        """
        初期化

        Args:
            client: J-Quants APIクライアント(省略時は新規作成)
            file_manager: ファイル管理クラス(省略時は新規作成)
        """
        self.client = client or create_client()
        self.file_manager = file_manager or FileManager()

    def fetch_and_save_financial_data(self, stock_codes: list[str]) -> None:
        """
        複数の証券コードの財務データを取得・保存

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
                df_fins = self._fetch_financial_data(code)

                # CSV保存
                self._save_to_csv(df_fins, code)
                new_count += 1

            except Exception:
                logger.exception(
                    "証券コード %s のデータ取得・保存に失敗しました",
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
            / DataType.FINS.value
            / f"{stock_code}_fins.csv"
        )
        return bool(csv_path.exists())

    def _fetch_financial_data(self, stock_code: str) -> pd.DataFrame:
        """APIから財務データを取得"""
        df = self.client.get_fins_statements(code=stock_code, date_yyyymmdd="")
        return pd.DataFrame(df)

    def _save_to_csv(self, df: pd.DataFrame, stock_code: str) -> Path:
        """DataFrameをCSVファイルとして保存"""
        result = self.file_manager.save_by_stock_code(
            df=df, stock_code=stock_code, data_type=DataType.FINS
        )
        return Path(result)
