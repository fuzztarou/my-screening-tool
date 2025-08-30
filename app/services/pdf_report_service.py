"""
PDFレポート生成サービス

複数のチャートを統合してPDFレポートを生成します。
"""

import logging
from pathlib import Path
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from app.services.analyze_quotes import StockMetrics
from app.utils.files import FileManager

logger = logging.getLogger(__name__)


class PdfReportService:
    """PDFレポートを生成するサービス"""

    def __init__(self, file_manager: Optional[FileManager] = None):
        self.file_manager = file_manager or FileManager()
        self._setup_matplotlib()

    def _setup_matplotlib(self) -> None:
        """matplotlibの設定"""
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            "DejaVu Sans",
            "Arial",
            "sans-serif",
        ]

    def _setup_x_axis(
        self,
        ax: plt.Axes,
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

    def create_comprehensive_report(self, stock_metrics: StockMetrics) -> Path:
        """4つのチャートを統合した包括的なPDFレポートを作成"""
        # PDFファイルのパスを設定
        date_str = self.file_manager.get_date_string(stock_metrics.analysis_date)
        date_dir = self.file_manager.base_dir / date_str
        self.file_manager.ensure_directory_exists(date_dir)

        date_short = date_str.replace("-", "")[2:]  # 2025-08-23 -> 250823
        pdf_path = (
            date_dir / f"{stock_metrics.code}_{date_short}_comprehensive_report.pdf"
        )

        try:
            # PDFに4つのチャートを統合
            with PdfPages(pdf_path) as pdf:
                # A4サイズ(8.27 x 11.69 inch)のページを作成
                fig = plt.figure(figsize=(8.27, 11.69))

                # 全体のタイトルを追加（英語のみでエンコード問題を回避）
                fig.suptitle(
                    f"{stock_metrics.code} - Comprehensive Analysis Report\n"
                    f"Analysis Date: {stock_metrics.analysis_date}",
                    fontsize=14,
                    fontweight="bold",
                    y=0.97,
                )

                # データの準備
                df = stock_metrics.df_result.copy()

                # 1. 株価チャート (上部)
                ax1 = plt.subplot2grid((4, 1), (0, 0))
                self._create_price_subplot(ax1, df)

                # 2. 指標チャート
                ax2 = plt.subplot2grid((4, 1), (1, 0))
                self._create_indicators_subplot(ax2, df)

                # 3. 出来高チャート
                ax3 = plt.subplot2grid((4, 1), (2, 0))
                self._create_volume_subplot(ax3, df)

                # 4. 利益チャート (下部)
                ax4 = plt.subplot2grid((4, 1), (3, 0))
                self._create_profit_subplot(ax4, stock_metrics)

                # レイアウトを調整
                plt.tight_layout(rect=(0, 0, 1, 0.95))

                # PDFに保存
                pdf.savefig(fig, bbox_inches="tight", dpi=150)
                plt.close(fig)

        except UnicodeEncodeError as e:
            logger.error("PDFエンコードエラー: %s", e)
            raise
        except Exception as e:
            logger.error("PDF生成エラー: %s", e)
            raise

        logger.info("包括的なPDFレポートを作成しました: %s", pdf_path)
        return pdf_path

    def _create_price_subplot(self, ax: plt.Axes, df: pd.DataFrame) -> None:
        """株価サブプロットを作成"""
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

        ax.set_title("Stock Price Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Price (JPY)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self._setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def _create_indicators_subplot(self, ax: plt.Axes, df: pd.DataFrame) -> None:
        """指標サブプロットを作成"""
        ax.plot(df["Date"], df["PER"], label="PER", color="blue", linewidth=1.5)
        ax.plot(df["Date"], df["PBR"], label="PBR", color="green", linewidth=1.5)
        ax.plot(df["Date"], df["ROE"] * 100, label="ROE(%)", color="red", linewidth=1.5)

        ax.set_title("Financial Indicators", fontsize=10, fontweight="bold")
        ax.set_ylabel("Ratio", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self._setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def _create_volume_subplot(self, ax: plt.Axes, df: pd.DataFrame) -> None:
        """出来高サブプロットを作成"""
        volume_10k = df["Volume"] / 10000
        volume_ma25 = df["Volume"].rolling(window=25, min_periods=1).mean() / 10000
        volume_ma75 = df["Volume"].rolling(window=75, min_periods=1).mean() / 10000

        ax.bar(df["Date"], volume_10k, alpha=0.6, label="Volume", width=1)
        ax.plot(
            df["Date"], volume_ma25, label="25-day MA", color="orange", linewidth=1.5
        )
        ax.plot(df["Date"], volume_ma75, label="75-day MA", color="red", linewidth=1.5)

        ax.set_title("Volume Trend", fontsize=10, fontweight="bold")
        ax.set_ylabel("Volume (10K)", fontsize=9)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)
        self._setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)

    def _create_profit_subplot(self, ax: plt.Axes, stock_metrics: StockMetrics) -> bool:
        """利益サブプロットを作成（stock_metricsの財務データを直接使用）"""
        try:
            df = stock_metrics.df_result.copy()

            # 利益データが存在するかチェック
            if "Profit" not in df.columns or df["Profit"].isna().all():
                ax.text(
                    0.5,
                    0.5,
                    "No profit data available",
                    transform=ax.transAxes,
                    ha="center",
                    va="center",
                    fontsize=10,
                    color="gray",
                )
                ax.set_title("Net Profit Trend", fontsize=10, fontweight="bold")
                return False

            # 日付データの型を確認し、必要に応じて変換
            if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
                df["Date"] = pd.to_datetime(df["Date"])

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

            # 予想利益をプロット（データが存在する場合）
            if (
                "ForecastProfit" in df.columns
                and df["ForecastProfit_100M"].notna().any()
            ):
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
            self._setup_x_axis(ax, minticks=2, maxticks=6, fontsize=8)
            return True

        except Exception as e:
            logger.warning("利益チャートの作成に失敗しました: %s", e)
            ax.text(
                0.5,
                0.5,
                "Error loading profit data",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=10,
                color="red",
            )
            ax.set_title("Net Profit Trend", fontsize=10, fontweight="bold")
            return False
