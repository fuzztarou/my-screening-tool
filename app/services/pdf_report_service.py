"""
PDFレポート生成サービス

複数のチャートを統合してPDFレポートを生成します。
"""

import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from app.services.analyze_quotes import StockMetrics
from app.services.chart_creator import ChartCreator
from app.utils.files import FileManager

logger = logging.getLogger(__name__)


class PdfReportService:
    """PDFレポートを生成するサービス"""

    def __init__(self, file_manager: Optional[FileManager] = None):
        self.file_manager = file_manager or FileManager()
        self.chart_creator = ChartCreator()
        self._setup_matplotlib()

    def _setup_matplotlib(self) -> None:
        """matplotlibの設定"""
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            "DejaVu Sans",
            "Arial",
            "sans-serif",
        ]

    def create_comprehensive_report(self, stock_metrics: StockMetrics) -> Path:
        """4つのチャートを統合した包括的なPDFレポートを作成"""
        # PDFファイルのパスを設定
        date_str = self.file_manager.get_date_string(stock_metrics.analysis_date)
        date_dir = self.file_manager.base_dir.parent / "outputs" / date_str
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

                # 1行目: 株価と出来高の統合チャート
                ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=2)
                self.chart_creator.create_price_chart_with_volume(ax1, df)

                # 2行目: 指標チャート
                ax2 = plt.subplot2grid((4, 2), (1, 0), colspan=2)
                self.chart_creator.create_indicators_chart(ax2, df)

                # 3行目: 左に売上チャート、右に営業利益チャート
                ax3 = plt.subplot2grid((4, 2), (2, 0))
                self.chart_creator.create_sales_chart(ax3, stock_metrics)

                ax4 = plt.subplot2grid((4, 2), (2, 1))
                self.chart_creator.create_operation_profit_chart(ax4, stock_metrics)

                # 4行目: 左に当期利益チャート、右は空欄
                ax5 = plt.subplot2grid((4, 2), (3, 0))
                self.chart_creator.create_profit_chart(ax5, stock_metrics)

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
