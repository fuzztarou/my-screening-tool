"""
チャート作成サービス

株価分析レポート用の各種チャートを作成します。
"""

import logging

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from app.services.analyze_quotes import StockMetrics
from app.services.plotter import Plotter

logger = logging.getLogger(__name__)


class ChartCreator:
    """チャート作成専用クラス"""

    def __init__(self) -> None:
        self.plotter = Plotter()

    def setup_x_axis(
        self,
        ax: Axes,
        minticks: int = 3,
        maxticks: int = 8,
        fontsize: int | None = None,
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
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_volume_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """出来高チャートを作成"""
        self.plotter.plot_volume_bars(ax, df)

        ax.set_title("Volume Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Volume (10K)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_price_chart_with_volume(self, ax: Axes, df: pd.DataFrame) -> None:
        """株価と出来高を統合したチャートを作成"""
        # 株価をプロット
        self.plotter.plot_price_lines(ax, df)

        # 右側に出来高チャート用のY軸を作成
        ax2: Axes = ax.twinx()  # type: ignore[assignment]

        # 出来高をプロット【右軸、透明度を下げて株価を見やすくする】
        self.plotter.plot_volume_bars(ax2, df, alpha=0.3)

        ax.set_title("Stock Price & Volume Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Price (JPY)", fontsize=9)
        ax2.set_ylabel("Volume (10K)", fontsize=9)

        # 凡例を結合（チャートの上に2行で配置）
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(
            lines1 + lines2,
            labels1 + labels2,
            loc="lower center",
            bbox_to_anchor=(0.5, 1.15),
            ncol=3,
            fontsize=6,
        )

        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_per_roe_roa_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """PER, ROE, ROA指標チャートを作成"""
        self.plotter.plot_per(ax, df)
        self.plotter.plot_roe(ax, df)
        self.plotter.plot_roa(ax, df)

        ax.set_title(
            "Financial Indicators (PER, ROE, ROA)", fontsize=10, fontweight="bold"
        )
        ax.set_ylabel("Ratio", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_pbr_psr_peg_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """PBR, PSR, PEG指標チャートを作成"""
        self.plotter.plot_pbr(ax, df)
        self.plotter.plot_psr(ax, df)
        self.plotter.plot_peg_ratio(ax, df)

        ax.set_title(
            "Financial Indicators (PBR, PSR, PEG)", fontsize=10, fontweight="bold"
        )
        ax.set_ylabel("Ratio", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_sales_chart(self, ax: Axes, stock_metrics: StockMetrics) -> None:
        """売上高チャートを作成"""
        df = stock_metrics.df_result.copy()
        self.plotter.plot_sales(ax, df)

        ax.set_title("Net Sales Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Net Sales (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_operation_profit_chart(
        self, ax: Axes, stock_metrics: StockMetrics
    ) -> None:
        """営業利益チャートを作成"""
        df = stock_metrics.df_result.copy()
        # 営業利益をプロット
        self.plotter.plot_operating_profit(ax, df)

        ax.set_title("Operating Profit Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Operating Profit (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_profit_chart(self, ax: Axes, stock_metrics: StockMetrics) -> None:
        """純利益チャートを作成"""
        df = stock_metrics.df_result.copy()
        # 純利益をプロット
        self.plotter.plot_net_profit(ax, df)

        ax.set_title("Net Profit Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Net Profit (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_peg_chart(self, ax: Axes, df: pd.DataFrame) -> None:
        """PEG Ratioチャートを作成"""
        self.plotter.plot_peg_ratio(ax, df)

        ax.set_title("PEG Ratio", fontsize=10, fontweight="bold")
        ax.set_ylabel("PEG Ratio", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_margin_chart(self, ax: Axes, stock_metrics: StockMetrics) -> None:
        """営業利益率と純利益率のチャートを作成"""
        df = stock_metrics.df_result.copy()

        # 営業利益率をプロット
        self.plotter.plot_operating_margin(ax, df)
        self.plotter.plot_forecast_operating_margin(ax, df)

        # 純利益率をプロット
        self.plotter.plot_net_margin(ax, df)
        self.plotter.plot_forecast_net_margin(ax, df)

        ax.set_title("Operating & Net Margin Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Margin (%)", fontsize=9)
        ax.legend(loc="upper left", fontsize=6)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def create_cash_flow_chart(self, ax: Axes, stock_metrics: StockMetrics) -> None:
        """キャッシュフローチャートを作成（営業・投資・財務CF、現金同等物、時価総額）"""
        df = stock_metrics.df_result.copy()
        self.plotter.plot_operating_cash_flow(ax, df)
        self.plotter.plot_investing_cash_flow(ax, df)
        self.plotter.plot_financing_cash_flow(ax, df)
        self.plotter.plot_cash_and_equivalents(ax, df)
        self.plotter.plot_market_cap(ax, df)

        ax.set_title("Cash Flow & Market Cap Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Amount (100M JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=6)
        ax.grid(visible=True, alpha=0.3)
        self.setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)
