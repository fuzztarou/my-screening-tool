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
from app.repository.listed_info import ListedInfoHandler
from app.utils.files import FileManager

logger = logging.getLogger(__name__)

# 財務データのフィルタリング用
FINS_COLUMNS_TO_EXTRACT = [
    "DisclosedDate",
    "LocalCode",
    "TypeOfDocument",
    "NetSales",
    "OperatingProfit",
    "OrdinaryProfit",
    "Profit",
    "EarningsPerShare",
    "ForecastNetSales",
    "ForecastOperatingProfit",
    "ForecastOrdinaryProfit",
    "ForecastProfit",
    "ForecastEarningsPerShare",
    "NextYearForecastNetSales",
    "NextYearForecastOperatingProfit",
    "NextYearForecastOrdinaryProfit",
    "NextYearForecastProfit",
    "NextYearForecastEarningsPerShare",
    "TotalAssets",
    "Equity",
    "EquityToAssetRatio",
    "BookValuePerShare",
    "NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock",
    "AverageNumberOfShares",
]

FINS_COLUMNS_TO_NUMERIC = [
    "NetSales",
    "OperatingProfit",
    "OrdinaryProfit",
    "Profit",
    "EarningsPerShare",
    "ForecastNetSales",
    "ForecastOperatingProfit",
    "ForecastOrdinaryProfit",
    "ForecastProfit",
    "ForecastEarningsPerShare",
    "NextYearForecastNetSales",
    "NextYearForecastOperatingProfit",
    "NextYearForecastOrdinaryProfit",
    "NextYearForecastProfit",
    "NextYearForecastEarningsPerShare",
    "TotalAssets",
    "Equity",
    "EquityToAssetRatio",
    "BookValuePerShare",
    "NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock",  # 発行済株式数
    "AverageNumberOfShares",
]


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
        processed_codes = []  # 5桁のLocalCodeを格納

        for code in stock_codes:
            try:
                # APIからデータ取得
                df_fins = self._fetch_financial_data(code)

                # APIデータから5桁のLocalCodeを取得
                if "LocalCode" in df_fins.columns and not df_fins.empty:
                    api_code = str(df_fins["LocalCode"].iloc[0])
                else:
                    api_code = code

                # 5桁のAPIコードでファイル存在チェック
                if self._csv_exists(api_code):
                    existing_count += 1
                    processed_codes.append(api_code)
                    continue

                # CSV保存（5桁のAPIコードを使用）
                self._save_to_csv(df_fins, api_code)
                new_count += 1
                processed_codes.append(api_code)

            except Exception:
                logger.exception(
                    "証券コード %s のデータ取得・保存に失敗しました",
                    code,
                )

        # 統合ファイルを作成（5桁のコードを使用）
        self._create_consolidated_file(processed_codes)

        # 上場企業情報ファイルを作成
        listed_info_handler = ListedInfoHandler(
            client=self.client, file_manager=self.file_manager
        )
        listed_info_handler.create_listed_info_file()

        # 最終結果をログで出力
        logger.info("既存CSV: %d個, 新規CSV: %d個", existing_count, new_count)

    def _csv_exists(self, stock_code: str) -> bool:
        """指定した証券コードのCSVファイルが存在するかチェック"""
        date_str = self.file_manager.get_date_string()
        # 日付を YYMMDD 形式で取得
        date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
        csv_path = (
            self.file_manager.base_dir
            / "temporary"
            / date_str
            / stock_code
            / f"{stock_code}_{date_short}_fins.csv"
        )
        return bool(csv_path.exists())

    def _fetch_financial_data(self, stock_code: str) -> pd.DataFrame:
        """APIから財務データを取得"""
        df = self.client.get_fins_statements(code=stock_code, date_yyyymmdd="")

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

    def _save_to_csv(self, df: pd.DataFrame, stock_code: str) -> Path:
        """DataFrameをCSVファイルとして保存（5桁のAPIコードを使用）"""
        date_str = self.file_manager.get_date_string()
        # 5桁のAPIコードでディレクトリとファイル名を作成
        code_dir = self.file_manager.base_dir / "temporary" / date_str / stock_code
        self.file_manager.ensure_directory_exists(code_dir)

        # 日付を YYMMDD 形式で取得
        date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
        file_path = code_dir / f"{stock_code}_{date_short}_fins.csv"
        df.to_csv(file_path, index=False)
        logger.info(
            "財務データを保存しました: %s (LocalCode: %s)", file_path, stock_code
        )
        return file_path

    def _create_consolidated_file(self, stock_codes: list[str]) -> None:
        """個別の財務ファイルを統合してfins_org.csvを作成"""
        try:
            date_str = self.file_manager.get_date_string()
            base_dir = self.file_manager.base_dir / "temporary" / date_str

            # 統合用のDataFrameリスト
            consolidated_dfs = []

            # 各証券コードのファイルを読み込み（新しいディレクトリ構造）
            date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
            for code in stock_codes:
                csv_path = base_dir / code / f"{code}_{date_short}_fins.csv"
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

                # 統合ファイルを保存（ルートディレクトリに）
                consolidated_path = base_dir / "fins_org.csv"
                consolidated_df.to_csv(consolidated_path, index=False)
                logger.info("統合ファイルを作成しました: %s", consolidated_path)
                logger.info("統合データ件数: %d件", len(consolidated_df))
            else:
                logger.warning("統合対象のファイルが見つかりませんでした")

        except Exception as e:
            logger.exception("統合ファイル作成中にエラーが発生しました: %s", e)
