"""
チャート作成サービス

株価分析レポート用の各種チャートを作成します。
"""

import logging
from typing import Optional
from matplotlib.axes import Axes

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from app.services.analyze_quotes import StockMetrics

logger = logging.getLogger(__name__)


class ChartCreator:
    """チャート作成専用クラス"""

    def setup_x_axis(
        self,
        ax: Axes,
        minticks: int = 3,
        maxticks: int = 8,
        fontsize: Optional[int] = None,
    ) -> None:
        """X軸の共通設定を適用"""
        ax.xaxis.set_major_locator(
            mpl.dates.AutoDateLocator(minticks=minticks, maxticks=maxticks)
        )
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%Y-%m"))
        ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        plt.setp(ax.get_xticklabels(), rotation=45, fontsize=fontsize)

    def _plot_price_lines(self, ax: Axes, df: pd.DataFrame) -> None:
        """株価の各種ラインをプロットする共通メソッド"""
        ax.plot(
            df["Date"],
            df["AdjustmentClose"],
            label="Stock Price",
            linewidth=1.5,
            color="blue",
        )
        ax.plot(
            df["Date"],
            df["TheoreticalStockPrice"],
            label="Theoretical Price",
            linestyle="--",
            linewidth=1,
            color="green",
        )
        ax.plot(
            df["Date"],
            df["TheoreticalStockPriceUpperLimit"],
            label="Theoretical Upper",
            linestyle=":",
            linewidth=1,
            color="red",
        )
        ax.plot(
            df["Date"],
            df["SMA_200"],
            label="200-day MA",
            alpha=0.7,
            linewidth=1,
            color="purple",
        )

    def _plot_volume_bars_and_lines(
        self, ax: Axes, df: pd.DataFrame, alpha: float = 0.6
    ) -> None:
        """出来高のバーと移動平均線をプロットする共通メソッド"""
        volume_10k = df["Volume"] / 10000
        volume_ma25 = df["Volume"].rolling(window=25, min_periods=1).mean() / 10000
        volume_ma75 = df["Volume"].rolling(window=75, min_periods=1).mean() / 10000

        ax.bar(df["Date"], volume_10k, alpha=alpha, label="Volume", width=1)
        ax.plot(
            df["Date"], volume_ma25, label="25-day MA", color="orange", linewidth=1.5
        )
        ax.plot(df["Date"], volume_ma75, label="75-day MA", color="red", linewidth=1.5)

    def create_price_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """株価チャートを作成"""
        self._plot_price_lines(ax, df)

        ax.set_title("Stock Price Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Price (JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_volume_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """出来高チャートを作成"""
        self._plot_volume_bars_and_lines(ax, df)

        ax.set_title("Volume Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Volume (10K)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_price_chart_with_volume(self, ax: Axes, df: pd.DataFrame) -> None:
        """株価と出来高を統合したチャートを作成"""
        # 株価をプロット
        self._plot_price_lines(ax, df)

        # 右側に出来高チャート用のY軸を作成
        ax2 = ax.twinx()

        # 出来高をプロット（右軸、透明度を下げて株価を見やすくする）
        self._plot_volume_bars_and_lines(ax2, df, alpha=0.3)  # type: ignore

        ax.set_title("Stock Price & Volume Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Price (JPY)", fontsize=9)
        ax2.set_ylabel("Volume (10K)", fontsize=9)  # type: ignore

        # 凡例を結合
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()  # type: ignore
        ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_indicators_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """指標チャートを作成"""
        ax.plot(df["Date"], df["PER"], label="PER", color="blue", linewidth=1.5)
        ax.plot(df["Date"], df["PBR"], label="PBR", color="green", linewidth=1.5)
        ax.plot(df["Date"], df["ROE"] * 100, label="ROE(%)", color="red", linewidth=1.5)

        ax.set_title("Financial Indicators", fontsize=10, fontweight="bold")
        ax.set_ylabel("Ratio", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_operation_profit_chart(
        self, ax: Axes, stock_metrics: StockMetrics
    ) -> None:
        """営業利益チャートを作成"""
        df = stock_metrics.df_result.copy()

        # 営業利益データを億円単位に変換
        df["OperatingProfit_100M"] = df["OperatingProfit"] / 1e8
        df["ForecastOperatingProfit_100M"] = df["ForecastOperatingProfit"] / 1e8

        # 実績営業利益をプロット
        ax.step(
            df["Date"],
            df["OperatingProfit_100M"],
            where="post",
            label="Operating Profit (Actual)",
            linewidth=1.5,
            color="green",
        )

        # 予想営業利益をプロット
        ax.step(
            df["Date"],
            df["ForecastOperatingProfit_100M"],
            where="post",
            label="Operating Profit (Forecast)",
            linestyle="--",
            linewidth=1.5,
            color="red",
            alpha=0.7,
        )

        ax.set_title("Operating Profit Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Operating Profit (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_profit_chart(self, ax: Axes, stock_metrics: StockMetrics) -> None:
        """利益チャートを作成（stock_metricsの財務データを直接使用）"""
        df = stock_metrics.df_result.copy()

        # 利益データを億円単位に変換
        df["Profit_100M"] = df["Profit"] / 1e8
        df["ForecastProfit_100M"] = df["ForecastProfit"] / 1e8

        # 実績利益をプロット
        ax.step(
            df["Date"],
            df["Profit_100M"],
            where="post",
            label="Net Profit (Actual)",
            linewidth=1.5,
            color="blue",
        )

        # 予想利益をプロット
        ax.step(
            df["Date"],
            df["ForecastProfit_100M"],
            where="post",
            label="Net Profit (Forecast)",
            linestyle="--",
            linewidth=1.5,
            color="red",
            alpha=0.7,
        )

        ax.set_title("Net Profit Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Net Profit (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)
