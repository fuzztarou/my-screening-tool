"""
チャート作成サービス

StockMetricsからチャートを生成するサービスを提供します。
"""

import datetime
import logging
from pathlib import Path
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from app.services.analyze_quotes import StockMetrics
from app.utils.files import FileManager

logger = logging.getLogger(__name__)


class ChartService:
    """StockMetricsからチャートを生成するサービス"""

    def __init__(self, file_manager: Optional[FileManager] = None):
        self.file_manager = file_manager or FileManager()
        self._setup_matplotlib()

    def _setup_matplotlib(self) -> None:
        """matplotlibの設定"""
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            "Hiragino Sans",
            "Yu Gothic",
            "Noto Sans CJK JP",
            "Meirio",
            "DejaVu Sans",
        ]
        # フォント警告を抑制
        import warnings

        warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
        warnings.filterwarnings("ignore", category=UserWarning, module="mplfinance")

    def _setup_x_axis(
        self,
        ax: mpl.axes.Axes,
        minticks: int = 3,
        maxticks: int = 8,
        fontsize: Optional[int] = None,
    ) -> None:
        """X軸の共通設定を適用"""
        ax.xaxis.set_major_locator(
            mpl.dates.AutoDateLocator(minticks=minticks, maxticks=maxticks)
        )
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%Y-%m"))
        plt.setp(ax.get_xticklabels(), rotation=45, fontsize=fontsize)

    def create_price_chart(self, stock_metrics: StockMetrics) -> Path:
        """株価チャートを作成（株価・理論株価・移動平均）"""
        df = stock_metrics.df_result.copy()
        title = f"{stock_metrics.code} {stock_metrics.company_name} - Stock Price Chart"

        # 日付データの型を確認し、必要に応じて変換
        if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = pd.to_datetime(df["Date"])

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle(title)

        # 株価、理論株価、理論株価上限、移動平均をプロット
        ax.plot(df["Date"], df["AdjustmentClose"], label="Stock Price", linewidth=2)
        ax.plot(
            df["Date"],
            df["TheoreticalStockPrice"],
            label="Theoretical Price",
            linestyle="--",
        )
        ax.plot(
            df["Date"],
            df["TheoreticalStockPriceUpperLimit"],
            label="Theoretical Price Upper",
            linestyle=":",
        )
        ax.plot(df["Date"], df["SMA_200"], label="200-day MA", alpha=0.7)

        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("Price (JPY)")

        # X軸のフォーマット
        self._setup_x_axis(ax)

        # 保存
        file_path = self._save_chart(
            fig,
            f"{stock_metrics.code}_price",
            stock_metrics.analysis_date,
            stock_metrics.code,
        )
        plt.close(fig)
        return file_path

    def create_indicators_chart(self, stock_metrics: StockMetrics) -> Path:
        """指標チャートを作成（PER・PBR・ROE）"""
        df = stock_metrics.df_result.copy()
        title = (
            f"{stock_metrics.code} {stock_metrics.company_name} - Financial Indicators"
        )

        # 日付データの型を確認し、必要に応じて変換
        if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = pd.to_datetime(df["Date"])

        # 1行1列のグラフ
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle(title)

        # PER、PBR、ROEを同一グラフに表示
        ax.plot(df["Date"], df["PER"], label="PER", color="blue")
        ax.plot(df["Date"], df["PBR"], label="PBR", color="green")
        ax.plot(df["Date"], df["ROE"] * 100, label="ROE", color="red")

        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("Ratio")

        # X軸のフォーマット
        self._setup_x_axis(ax, minticks=2, maxticks=5)

        plt.tight_layout()

        # 保存
        file_path = self._save_chart(
            fig,
            f"{stock_metrics.code}_indicators",
            stock_metrics.analysis_date,
            stock_metrics.code,
        )
        plt.close(fig)
        return file_path

    def create_volume_chart(self, stock_metrics: StockMetrics) -> Path:
        """出来高チャートを作成"""
        df = stock_metrics.df_result.copy()
        title = f"{stock_metrics.code} {stock_metrics.company_name} - Volume Chart"

        # 日付データの型を確認し、必要に応じて変換
        if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = pd.to_datetime(df["Date"])

        fig, ax = plt.subplots(figsize=(12, 4))
        fig.suptitle(title)

        # 出来高を万株単位で表示
        volume_10k = df["Volume"] / 10000
        smoothed_volume_10k = df["Smoothed_volume"] / 10000

        ax.bar(df["Date"], volume_10k, alpha=0.6, label="Volume", width=1)
        ax.plot(
            df["Date"],
            smoothed_volume_10k,
            label="Volume MA",
            color="red",
            linewidth=2,
        )

        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("Volume (10K shares)")

        # X軸のフォーマット
        self._setup_x_axis(ax)

        # 保存
        file_path = self._save_chart(
            fig,
            f"{stock_metrics.code}_volume",
            stock_metrics.analysis_date,
            stock_metrics.code,
        )
        plt.close(fig)
        return file_path

    def create_candlestick_chart(
        self, stock_metrics: StockMetrics, days: int = 60
    ) -> Path:
        """ローソクチャートを作成"""
        df = stock_metrics.df_result.tail(days).copy()

        # 日付データの型を確認し、必要に応じて変換
        if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = pd.to_datetime(df["Date"])

        # Dateをインデックスに設定
        df.set_index("Date", inplace=True)

        # mplfinance用にカラム名を設定
        df["Open"] = df["AdjustmentOpen"]
        df["High"] = df["AdjustmentHigh"]
        df["Low"] = df["AdjustmentLow"]
        df["Close"] = df["AdjustmentClose"]

        # 保存設定
        date_str = self.file_manager.get_date_string(stock_metrics.analysis_date)
        code_dir = (
            self.file_manager.base_dir / "temporary" / date_str / stock_metrics.code
        )
        self.file_manager.ensure_directory_exists(code_dir)

        # 日付を YYMMDD 形式で取得
        date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
        file_path = code_dir / f"{stock_metrics.code}_{date_short}_candlestick.png"
        save_settings = {"fname": str(file_path), "dpi": 100, "pad_inches": 0.25}

        # ローソクチャートを作成
        mpf.plot(
            df,
            type="candle",
            volume=True,
            mav=(5, 25),
            style="charles",
            title=f"{stock_metrics.code} {stock_metrics.company_name} - Candlestick Chart ({days} days)",
            savefig=save_settings,
        )

        return file_path

    def create_stock_price_chart(self, stock_metrics: StockMetrics) -> Path:
        """株価総合チャートを作成（株価関連データのみ）"""
        df = stock_metrics.df_result.copy()
        title = f"{stock_metrics.code} {stock_metrics.company_name} - Comprehensive Stock Chart"

        # 日付データの型を確認し、必要に応じて変換
        if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = pd.to_datetime(df["Date"])

        # 1行1列のグラフを作成
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle(title)

        # 株価関連データを表示
        ax.plot(
            df["Date"],
            df["AdjustmentClose"],
            label="Stock Price",
            linewidth=2,
            color="black",
        )
        ax.plot(
            df["Date"],
            df["TheoreticalStockPrice"],
            label="Theoretical Price",
            linestyle="--",
            color="orange",
        )
        ax.plot(
            df["Date"],
            df["TheoreticalStockPriceUpperLimit"],
            label="Theoretical Price Upper",
            linestyle=":",
            color="red",
        )
        ax.plot(
            df["Date"], df["SMA_200"], label="200-day MA", alpha=0.7, color="purple"
        )

        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("Price (JPY)")

        # X軸のフォーマット
        self._setup_x_axis(ax, minticks=2, maxticks=7)

        plt.tight_layout()

        # 保存
        file_path = self._save_chart(
            fig,
            f"{stock_metrics.code}_stock_price",
            stock_metrics.analysis_date,
            stock_metrics.code,
        )
        plt.close(fig)
        return file_path

    def _save_chart(
        self, fig: plt.Figure, filename: str, date: datetime.date, code: str
    ) -> Path:
        """チャートを保存"""
        date_str = self.file_manager.get_date_string(date)
        code_dir = self.file_manager.base_dir / "temporary" / date_str / code
        self.file_manager.ensure_directory_exists(code_dir)

        # 日付を YYMMDD 形式で取得
        date_short = date_str.replace("-", "")[2:]  # 2025-08-12 -> 250812
        file_path = code_dir / f"{code}_{date_short}_{filename.split('_', 1)[1]}.png"
        fig.savefig(file_path, dpi=100, bbox_inches="tight")
        logger.info("チャートを保存しました: %s", file_path)
        return file_path
