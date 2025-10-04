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
from app.types import RawFinancialData, RawQuotesData

logger = logging.getLogger(__name__)


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
        df = self._set_AdjustmentBPS_value(df)
        df = self._set_PER_value(df)
        df = self._set_PBR_value(df)
        df = self._set_ROE_value(df)
        df = self._set_ROA_value(df)
        df = self._set_market_cap(df)
        df = self._set_smoothed_volume(df)
        df = self._set_200days_moving_average(df)
        return df

    def calculate_theoretical_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """理論株価を計算"""
        df = self._set_discount_rate(df)
        df = self._limit_ROA_value(df)
        df = self._set_risk_assessment_rate(df)
        df = self._set_financial_leverage_adjustment(df)
        df = self._set_asset_value(df)
        df = self._set_business_value(df)
        df = self._set_theoretical_stock_price(df)
        return df

    def _set_AdjustmentBPS_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """最新の[期中平均株式数]で値を計算"""
        AverageNumberOfShares = df["AverageNumberOfShares"].iloc[-1]
        df["AdjustmentBPS"] = df["Equity"] / AverageNumberOfShares
        return df

    def _set_PER_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """PER値を計算(株式分割されると値がジャンプするので最新の発行済株数で計算)"""
        AverageNumberOfShares = df["AverageNumberOfShares"].iloc[-1]
        df["PER"] = df["AdjustmentClose"] / (
            df["ForecastProfit"] / AverageNumberOfShares
        )
        return df

    def _set_PBR_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """PBR値を計算(株式分割されると値がジャンプするので最新の発行済株数で計算)"""
        AverageNumberOfShares = df["AverageNumberOfShares"].iloc[-1]
        df["PBR"] = df["AdjustmentClose"] / (df["Equity"] / AverageNumberOfShares)
        return df

    def _set_ROE_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """ROE値を計算(割っただけの値)"""
        df["ROE"] = df["ForecastProfit"] / df["Equity"]
        return df

    def _set_ROA_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """ROAを計算(割っただけの値)"""
        df["ROA"] = df["ForecastProfit"] / df["TotalAssets"]
        return df

    def _set_market_cap(self, df: pd.DataFrame) -> pd.DataFrame:
        """時価総額を計算"""
        df["MarketCap"] = df["AdjustmentClose"] * df["AverageNumberOfShares"]
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
        df["AssetValue"] = df["AdjustmentBPS"] * df["DiscountRate"]
        return df

    def _set_business_value(self, df: pd.DataFrame) -> pd.DataFrame:
        """事業価値を計算(株式分割されると値がジャンプするので最新の発行済株数で計算)"""
        AverageNumberOfShares = df["AverageNumberOfShares"].iloc[-1]
        df["BusinessValue"] = (
            df["ForecastProfit"]
            / AverageNumberOfShares
            * df["ROA"]
            * 150
            * df["FinancialLeverageAdjustment"]
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
        self.df_fins: Optional[RawFinancialData] = None
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
        logger.info("株価分析処理を開始します（対象: %d銘柄）", len(codes))

        # 財務データを読み込み
        self.load_fins_data(date)

        results = []
        for i, code in enumerate(codes, start=1):
            stock_metrics = self._analyze_single_stock(code, i, len(codes))
            if stock_metrics is not None:
                results.append(stock_metrics)

        logger.info("株価分析処理が完了しました（成功: %d銘柄）", len(results))
        return results

    def _analyze_single_stock(
        self, code: str, index: int, total: int
    ) -> Optional[StockMetrics]:
        """
        単一銘柄の分析を実行

        Args:
            code: 銘柄コード
            index: 現在の処理番号（1始まり）
            total: 総銘柄数

        Returns:
            分析結果。失敗時はNone
        """
        try:
            logger.info("分析中: %s (%s/%s)", code, index, total)

            # 株価データ読み込み
            df_quotes = self._load_stock_quotes(code)

            # データマージ
            df_merged = self._merge_fins_and_stock(code, df_quotes)

            # 指標計算
            df_calculated = self.calculator.calculate_all_indicators(df_merged)

            # 理論株価計算
            df_result = self.calculator.calculate_theoretical_price(df_calculated)

            # 結果構築
            company_name = self.code_name_dict.get(code, code)
            assert self.target_date is not None, "分析日が設定されていません"
            stock_metrics = StockMetrics(
                code=code,
                company_name=company_name,
                df_merged=df_merged,
                df_calculated=df_calculated,
                df_result=df_result,
                analysis_date=self.target_date,
            )

            # キャッシュ
            self.analysis_cache[code] = stock_metrics
            return stock_metrics

        except Exception as e:
            logger.exception("銘柄 %s の分析に失敗: %s", code, e)
            return None

    def load_fins_data(self, date: datetime.date) -> None:
        """財務データを読み込み"""
        self.target_date = date
        date_str = self.file_manager.get_date_string(date)

        # 財務情報を読み込み（バリデーション・数値変換を含む）
        fins_path = self.file_manager.base_dir / "temporary" / date_str / "fins_org.csv"
        self.df_fins = RawFinancialData.from_csv(str(fins_path))

        # 銘柄辞書を作成
        self.code_name_dict = self._make_code_company_name_dict(date)

    def _load_stock_quotes(self, code: str) -> pd.DataFrame:
        """株価データを読み込み"""
        assert self.target_date is not None, "分析日が設定されていません"

        # 株価情報を読み込み
        date_str = self.file_manager.get_date_string(self.target_date)
        # 日付を YYMMDD 形式で取得
        date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
        quotes_path = (
            self.file_manager.base_dir
            / "temporary"
            / date_str
            / code
            / f"{code}_{date_short}_quotes.csv"
        )

        # 株価データを読み込み（バリデーション・数値変換を含む）
        quotes_data = RawQuotesData.from_csv(str(quotes_path))

        return quotes_data.df

    def _merge_fins_and_stock(self, code: str, df_quotes: pd.DataFrame) -> pd.DataFrame:
        """財務データと株価データをマージ"""
        # Noneチェック
        assert self.df_fins is not None, "財務データが読み込まれていません"

        # codeの財務情報だけを抽出（LocalCodeは文字列として比較）
        df_fins_extracted = self.df_fins.df[self.df_fins.df["LocalCode"] == str(code)].copy()

        # 財務データが存在しない場合は株価データをそのまま返す
        if df_fins_extracted.empty:
            logger.warning("コード %s の財務データが見つかりません", code)
            return df_quotes

        # 日付カラムをdatetime型に変換
        df_fins_extracted["DisclosedDate"] = pd.to_datetime(
            df_fins_extracted["DisclosedDate"]
        )
        df_quotes["Date"] = pd.to_datetime(df_quotes["Date"])

        # 財務データを日付でソート
        df_fins_extracted = df_fins_extracted.sort_values("DisclosedDate")

        # 株価データも日付でソート
        df_quotes = df_quotes.sort_values("Date")

        # merge_asof を使用して、各株価日付に対して最新の財務データをマージ
        # 株価の日付以前の最新の財務データを結合
        df_merged = pd.merge_asof(
            df_quotes,
            df_fins_extracted,
            left_on="Date",
            right_on="DisclosedDate",
            direction="backward",
        )

        # それでも欠損値がある場合（最初の財務データより前の株価データ）は前方補完
        df_merged.ffill(inplace=True)
        # まだ欠損値がある場合は後方補完
        df_merged.bfill(inplace=True)

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
