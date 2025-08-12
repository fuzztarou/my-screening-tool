"""
株価分析・レポート生成サービス

クラスベースの株価分析システムを提供します。
財務データと株価データを統合し、各種指標計算、理論株価算出を行います。
"""

import datetime
import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from app.utils.files import FileManager

logger = logging.getLogger(__name__)

# 長すぎるカラム名
LATEST_SHARES = (
    "NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock"
)


@dataclass
class StockMetrics:
    """株価指標データを保持するコンテナ"""

    code: str
    company_name: str
    df_merged: pd.DataFrame
    df_calculated: pd.DataFrame
    df_result: pd.DataFrame
    analysis_date: datetime.date


class IndicatorCalculator:
    """指標計算専門クラス"""

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """全ての指標を計算"""
        df = self._set_EPS_value(df)
        df = self._set_BPS_value(df)
        df = self._set_PER_value(df)
        df = self._set_PBR_value(df)
        df = self._set_ROE_value(df)
        df = self._set_market_cap(df)
        df = self._set_smoothed_volume(df)
        df = self._set_200days_moving_average(df)
        return df

    def calculate_theoretical_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """理論株価を計算"""
        df = self._set_discount_rate(df)
        df = self._set_ROA(df)
        df = self._limit_ROA_value(df)
        df = self._set_risk_assessment_rate(df)
        df = self._set_financial_leverage_adjustment(df)
        df = self._set_asset_value(df)
        df = self._set_business_value(df)
        df = self._set_theoretical_stock_price(df)
        return df

    def _set_EPS_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """EPS値を計算"""
        df["EPS"] = df["ForecastProfit"] / df[LATEST_SHARES].iloc[-1]
        return df

    def _set_PER_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """PER値を計算"""
        df["PER"] = df["AdjustmentClose"] / (df["EPS"])
        return df

    def _set_BPS_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """BPS値を計算"""
        df["BPS"] = df["Equity"] / df[LATEST_SHARES].iloc[-1]
        return df

    def _set_PBR_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """PBR値を計算"""
        df["PBR"] = df["AdjustmentClose"] / (df["BPS"])
        return df

    def _set_ROE_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """ROE値を計算(割っただけの値)"""
        df["ROE"] = df["ForecastProfit"] / df["Equity"]
        return df

    def _set_market_cap(self, df: pd.DataFrame) -> pd.DataFrame:
        """時価総額を計算"""
        df["MarketCap"] = df["AdjustmentClose"] * df["AverageNumberOfShares"]
        return df

    def _set_ROA(self, df: pd.DataFrame) -> pd.DataFrame:
        """ROAを計算(割っただけの値)"""
        df["ROA"] = df["ForecastProfit"] / df["TotalAssets"]
        return df

    def _limit_ROA_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """理論株価を計算する時にROAが 0.3 を超える場合は 0.3 としているため"""
        conditions = [df["ROA"] >= 0.3]
        choices = [0.3]
        df["ROA_Capped"] = np.select(conditions, choices, default=df["ROA"])
        return df

    def _set_discount_rate(self, df: pd.DataFrame) -> pd.DataFrame:
        """自己資本比率を基準に割引率を計算"""
        conditions = [
            df["EquityToAssetRatio"] >= 0.8,
            (df["EquityToAssetRatio"] >= 0.67) & (df["EquityToAssetRatio"] < 0.8),
            (df["EquityToAssetRatio"] >= 0.5) & (df["EquityToAssetRatio"] < 0.67),
            (df["EquityToAssetRatio"] >= 0.33) & (df["EquityToAssetRatio"] < 0.5),
            (df["EquityToAssetRatio"] >= 0.1) & (df["EquityToAssetRatio"] < 0.33),
            (df["EquityToAssetRatio"] < 0.1),
        ]
        choices = [0.8, 0.75, 0.7, 0.65, 0.6, 0.5]
        df["DiscountRate"] = np.select(conditions, choices, default=np.nan)
        return df

    def _set_financial_leverage_adjustment(self, df: pd.DataFrame) -> pd.DataFrame:
        """自己資本比率を基に財務レバレッジ調整を計算"""
        df["TempValue"] = df["EquityToAssetRatio"] + 0.33

        conditions = [
            df["TempValue"] <= 0.66,
            df["TempValue"] >= 1.00,
        ]
        choices = [0.66, 1.00]

        df["TempValue"] = np.select(conditions, choices, default=df["TempValue"])
        df["FinancialLeverageAdjustment"] = 1 / df["TempValue"]
        df = df.drop(columns=["TempValue"])
        return df

    def _set_risk_assessment_rate(self, df: pd.DataFrame) -> pd.DataFrame:
        """リスク評価率を計算"""
        conditions = [
            df["PBR"] >= 0.5,
            (df["PBR"] >= 0.41) & (df["PBR"] < 0.49),
            (df["PBR"] >= 0.34) & (df["PBR"] < 0.40),
            (df["PBR"] >= 0.25) & (df["PBR"] < 0.33),
            (df["PBR"] >= 0.21) & (df["PBR"] < 0.25),
            (df["PBR"] >= 0.04) & (df["PBR"] < 0.20),
            df["PBR"] < 0.04,
        ]
        choices = [1, 0.8, 0.66, 0.50, 0.33, 0.15, 0.02]
        df["RiskAssessmentRate"] = np.select(conditions, choices, default=np.nan)
        return df

    def _set_asset_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """資産価値を計算"""
        df["AssetValue"] = df["BPS"] * df["DiscountRate"]
        return df

    def _set_business_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """事業価値を計算"""
        df["BusinessValue"] = (
            df["EPS"] * df["ROA"] * 150 * df["FinancialLeverageAdjustment"]
        )
        return df

    def _set_theoretical_stock_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """理論株価を計算"""
        df["TheoreticalStockPrice"] = (df["BusinessValue"] + df["AssetValue"]) * df[
            "RiskAssessmentRate"
        ]
        df["TheoreticalStockPriceUpperLimit"] = df["TheoreticalStockPrice"] * 2
        return df

    def _set_200days_moving_average(self, df: pd.DataFrame) -> pd.DataFrame:
        """200日移動平均を計算"""
        df["SMA_200"] = df["AdjustmentClose"].rolling(window=200).mean()
        return df

    def _set_smoothed_volume(
        self, df: pd.DataFrame, window_size: int = 20
    ) -> pd.DataFrame:
        """出来高の移動平均を計算"""
        df["Smoothed_volume"] = df["Volume"].rolling(window=window_size).mean()
        return df


class StockDataProcessor:
    """株価データ処理メインクラス"""

    def __init__(self, file_manager: Optional[FileManager] = None):
        self.file_manager = file_manager or FileManager()
        self.calculator = IndicatorCalculator()

        # データを保持するインスタンス変数
        self.df_fins: Optional[pd.DataFrame] = None
        self.code_name_dict: dict = {}
        self.target_date: Optional[datetime.date] = None
        self.analysis_cache: dict[str, StockMetrics] = {}

    def process_quotes(
        self, codes: list[str], date: datetime.date
    ) -> list[StockMetrics]:
        """
        メイン分析処理

        Args:
            codes: 銘柄コードのリスト
            date: 分析対象日

        Returns:
            処理結果のリスト
        """
        logger.info("=== Analyze quotes ===")

        # 基本データを読み込み
        self.load_fins_data(date)

        results = []
        for i, code in enumerate(codes, start=1):
            try:
                logger.info("分析中: %s (%s/%s)", code, i, len(codes))
                result = self.process_stock(code)
                results.append(result)
            except Exception as e:
                logger.exception("銘柄 %s の分析に失敗: %s", code, e)

        return results

    def load_fins_data(self, date: datetime.date) -> None:
        """財務データを読み込み"""
        self.target_date = date
        date_str = self.file_manager.get_date_string(date)

        # 財務情報を読み込み
        fins_path = (
            self.file_manager.base_dir
            / "temporary"
            / date_str
            / "fins"
            / "fins_org.csv"
        )
        self.df_fins = pd.read_csv(fins_path, dtype={2: str})

        # 銘柄辞書を作成
        self.code_name_dict = self._make_code_company_name_dict(date)

    def process_stock(self, code: str) -> StockMetrics:
        """
        単一銘柄の分析

        Args:
            code: 銘柄コード

        Returns:
            分析結果データ
        """
        # データマージ
        df_merged = self._merge_fins_and_stock(code)

        # 指標計算
        df_calculated = self.calculator.calculate_all_indicators(df_merged)

        # 理論株価計算
        df_result = self.calculator.calculate_theoretical_price(df_calculated)

        # 結果をキャッシュ
        company_name = self.code_name_dict.get(code, code)
        assert self.target_date is not None, "分析日が設定されていません"
        stock_metrics = StockMetrics(
            code=code,
            company_name=company_name,
            df_merged=df_merged,
            df_calculated=df_calculated,
            df_result=df_result,
            analysis_date=self.target_date,  # type: ignore
        )

        self.analysis_cache[code] = stock_metrics
        return stock_metrics

    def _merge_fins_and_stock(self, code: str) -> pd.DataFrame:
        """株価情報と財務情報を結合"""
        # Noneチェック
        assert self.df_fins is not None, "財務データが読み込まれていません"
        assert self.target_date is not None, "分析日が設定されていません"

        # codeの財務情報だけを抽出
        df_fins_extracted = self.df_fins[self.df_fins["LocalCode"] == code]

        # 株価情報を読み込み
        date_str = self.file_manager.get_date_string(self.target_date)
        quotes_path = (
            self.file_manager.base_dir
            / "temporary"
            / date_str
            / "quotes"
            / f"{code}_quotes.csv"
        )
        df_quotes = pd.read_csv(quotes_path)

        # 財務情報と株価情報を結合
        df_merged = pd.merge(
            df_quotes,
            df_fins_extracted,
            left_on="Date",
            right_on="DisclosedDate",
            how="left",
        )

        # 欠損値を補完
        df_merged = df_merged.ffill()

        return df_merged

    def _make_code_company_name_dict(self, date: datetime.date) -> dict:
        """銘柄コードと会社名の対応を辞書型で返す"""
        date_str = self.file_manager.get_date_string(date)
        listed_path = (
            self.file_manager.base_dir / "temporary" / date_str / "listed_info.csv"
        )

        df_listed = pd.read_csv(listed_path)
        return dict(zip(df_listed["Code"], df_listed["CompanyName"]))


# 後方互換性のための関数インターフェース
def process_quotes(codes: list[str]) -> None:
    """
    後方互換性のためのラッパー関数

    Args:
        codes: 銘柄コードのリスト
    """
    analyzer = StockDataProcessor()
    # TODO: 日付の取得方法を設定から取得するように修正が必要
    date = datetime.date.today()
    analyzer.process_quotes(codes, date)
