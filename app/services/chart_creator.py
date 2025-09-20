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
from app.services.plotter import Plotter

logger = logging.getLogger(__name__)


class ChartCreator:
    """チャート作成専用クラス"""

    def __init__(self):
        self.plotter = Plotter()

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

    def create_price_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """株価チャートを作成"""
        self.plotter.plot_price_lines(ax, df)

        ax.set_title("Stock Price Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Price (JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_volume_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """出来高チャートを作成"""
        self.plotter.plot_volume_bars(ax, df)

        ax.set_title("Volume Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Volume (10K)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_price_chart_with_volume(self, ax: Axes, df: pd.DataFrame) -> None:
        """株価と出来高を統合したチャートを作成"""
        # 株価をプロット
        self.plotter.plot_price_lines(ax, df)

        # 右側に出来高チャート用のY軸を作成
        ax2 = ax.twinx()

        # 出来高をプロット（右軸、透明度を下げて株価を見やすくする）
        self.plotter.plot_volume_bars(ax2, df, alpha=0.3)  # type: ignore

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
        self.plotter.plot_per(ax, df)
        self.plotter.plot_pbr(ax, df)
        self.plotter.plot_roe(ax, df)
        self.plotter.plot_roa(ax, df)

        ax.set_title("Financial Indicators", fontsize=10, fontweight="bold")
        ax.set_ylabel("Ratio", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_sales_chart(self, ax: Axes, stock_metrics: StockMetrics) -> None:
        """売上高チャートを作成"""
        df = stock_metrics.df_result.copy()
        self.plotter.plot_sales(ax, df)

        ax.set_title("Net Sales Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Net Sales (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_operation_profit_chart(
        self, ax: Axes, stock_metrics: StockMetrics
    ) -> None:
        """営業利益チャートを作成"""
        df = stock_metrics.df_result.copy()
        self.plotter.plot_operating_profit(ax, df)

        ax.set_title("Operating Profit Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Operating Profit (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_profit_chart(self, ax: Axes, stock_metrics: StockMetrics) -> None:
        """利益チャートを作成（stock_metricsの財務データを直接使用）"""
        df = stock_metrics.df_result.copy()
        self.plotter.plot_net_profit(ax, df)

        ax.set_title("Net Profit Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Net Profit (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)
