"""
財務データハンドラー

複数の証券コードの財務データを取得し、CSVファイルとして保存するサービスを提供します。
将来的には財務データの分析機能も提供予定です。
"""

import logging
from pathlib import Path

import jquantsapi
import pandas as pd

from app.client.jq import create_client
from app.constants import FINS_COLUMNS_TO_EXTRACT
from app.utils.files import DATA_TYPE_FINS, FileManager

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

    def prepare_financial_data(self, normalized_codes: list[str]) -> None:
        """
        複数の証券コードの財務データを準備

        Args:
            normalized_codes: 正規化済み証券コードのリスト
        """
        logger.info(
            "財務データの取得・保存を開始します（対象: %d銘柄）", len(normalized_codes)
        )

        existing_count = 0
        new_count = 0

        for i, normalized_code in enumerate(normalized_codes):
            try:
                is_new = self._ensure_financial_csv(normalized_code)

                if is_new:
                    new_count += 1
                else:
                    existing_count += 1

            except Exception:
                logger.exception(
                    "証券コード %s のデータ取得・保存に失敗しました",
                    normalized_codes[i],
                )

        # 統合ファイルを作成（5桁のコードを使用）
        self._create_fins_targets_file(normalized_codes)

        # 最終結果をログで出力
        logger.info(
            "財務データ取得完了 - 既存CSV: %d個, 新規CSV: %d個",
            existing_count,
            new_count,
        )

    def _ensure_financial_csv(self, normalized_code: str) -> bool:
        """
        指定銘柄の財務データCSVの存在を保証

        Args:
            normalized_code: 正規化済み証券コード（5桁）

        Returns:
            新規作成フラグ: True=新規作成, False=既存ファイル

        Raises:
            Exception: データ取得・保存に失敗した場合
        """
        # 正規化されたコードでファイル存在チェック
        if self._csv_exists(normalized_code):
            return False

        # APIからデータ取得
        df_fins = self._fetch_financial_data(normalized_code)

        # CSV保存（正規化されたコードを使用）
        self._save_to_csv(df_fins, normalized_code)

        return True

    def _csv_exists(self, normalized_code: str) -> bool:
        """指定した証券コードのCSVファイルが存在するかチェック"""
        csv_path = self.file_manager.get_stock_data_path(normalized_code, DATA_TYPE_FINS)
        return bool(csv_path.exists())

    def _fetch_financial_data(self, normalized_code: str) -> pd.DataFrame:
        """APIから財務データを取得"""
        df = self.client.get_fins_statements(code=normalized_code, date_yyyymmdd="")

        # 日付でソート（重要！）
        df = df.sort_values("DisclosedDate").reset_index(drop=True)

        # 必要なカラムのみ抽出
        df = df[FINS_COLUMNS_TO_EXTRACT]

        # 空文字列をNaNに変換
        df = df.replace("", pd.NA)

        # 欠損値の処理
        # 日付が古いものがあればそれで埋める なければ日付が新しいもので埋める
        df.ffill(inplace=True)
        df.bfill(inplace=True)

        return df

    def _save_to_csv(self, df: pd.DataFrame, normalized_code: str) -> Path:
        """DataFrameをCSVファイルとして保存（5桁のAPIコードを使用）"""
        file_path = self.file_manager.get_stock_data_path(normalized_code, DATA_TYPE_FINS)
        self.file_manager.ensure_directory_exists(file_path.parent)

        df.to_csv(file_path, index=False)
        logger.info(
            "財務データを保存しました: %s (LocalCode: %s)", file_path, normalized_code
        )
        return file_path

    def _create_fins_targets_file(self, normalized_codes: list[str]) -> None:
        """個別の財務ファイルを統合してfins_targets.csvを作成"""
        try:
            # 統合用のDataFrameリスト
            consolidated_dfs = []

            # 各証券コードのファイルを読み込み
            for normalized_code in normalized_codes:
                csv_path = self.file_manager.get_stock_data_path(normalized_code, DATA_TYPE_FINS)
                if csv_path.exists():
                    try:
                        df = pd.read_csv(
                            csv_path, dtype={"LocalCode": str}
                        )  # LocalCodeを文字列として読み込み
                        consolidated_dfs.append(df)
                        logger.debug("統合ファイルに追加: %s", csv_path)
                    except Exception as e:
                        logger.warning("ファイル読み込みエラー %s: %s", csv_path, e)

            # 統合ファイルを作成
            if consolidated_dfs:
                consolidated_df = pd.concat(consolidated_dfs, ignore_index=True)

                # 統合ファイルを保存
                consolidated_path = self.file_manager.get_fins_targets_path()
                self.file_manager.ensure_directory_exists(consolidated_path.parent)
                consolidated_df.to_csv(consolidated_path, index=False)
                logger.info("統合ファイルを作成しました: %s", consolidated_path)
                logger.info("統合データ件数: %d件", len(consolidated_df))
            else:
                logger.warning("統合対象のファイルが見つかりませんでした")

        except Exception as e:
            logger.exception("統合ファイル作成中にエラーが発生しました: %s", e)
