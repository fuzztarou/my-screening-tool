"""
PDFレポート生成サービス

複数のチャートを統合してPDFレポートを生成します。
"""

import datetime
import io
import logging
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link

from app.services.analyze_quotes import StockMetrics
from app.services.chart_creator import ChartCreator
from app.utils.files import FileManager

logger = logging.getLogger(__name__)


class PdfReportService:
    """PDFレポートを生成するサービス"""

    def __init__(self, file_manager: FileManager | None = None):
        self.file_manager = file_manager or FileManager()
        self.chart_creator = ChartCreator()
        self._setup_matplotlib()

    def _setup_matplotlib(self) -> None:
        """matplotlibの設定"""
        # fonttools の詳細ログを抑制
        logging.getLogger("fontTools").setLevel(logging.ERROR)
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            "Hiragino Sans",
            "Hiragino Kaku Gothic Pro",
            "Yu Gothic",
            "DejaVu Sans",
            "Arial",
            "sans-serif",
        ]
        # PDF出力時にTrueTypeフォントを使用（日本語文字の埋め込み用）
        plt.rcParams["pdf.fonttype"] = 42

    def _create_report_page(self, pdf: PdfPages, stock_metrics: StockMetrics) -> None:
        """1銘柄分のレポートページを作成してPDFに追加

        Args:
            pdf: PdfPagesオブジェクト
            stock_metrics: 銘柄の分析データ
        """
        # A4サイズ(8.27 x 11.69 inch)のページを作成
        fig = plt.figure(figsize=(8.27, 11.69))

        # 全体のタイトルを追加
        fig.suptitle(
            f"{stock_metrics.code} {stock_metrics.company_name}\n"
            f"Analysis Date: {stock_metrics.analysis_date}",
            fontsize=14,
            fontweight="bold",
            y=0.97,
        )

        # データの準備
        df = stock_metrics.df_result.copy()

        # 1行目: 株価と出来高の統合チャート（左側に配置）
        ax1 = plt.subplot2grid((4, 2), (0, 0))
        self.chart_creator.create_price_chart_with_volume(ax1, df)

        # 2行目: 左にPER/ROE/ROA、右にPBR/PSR
        ax2 = plt.subplot2grid((4, 2), (1, 0))
        self.chart_creator.create_per_roe_roa_chart(ax2, df)

        ax3 = plt.subplot2grid((4, 2), (1, 1))
        self.chart_creator.create_pbr_psr_peg_chart(ax3, df)

        # 3行目: 左に売上チャート、右に営業利益チャート
        ax4 = plt.subplot2grid((4, 2), (2, 0))
        self.chart_creator.create_sales_chart(ax4, stock_metrics)

        ax5 = plt.subplot2grid((4, 2), (2, 1))
        self.chart_creator.create_operation_profit_chart(ax5, stock_metrics)

        # 4行目: 左に当期利益チャート、右にマージンチャート
        ax6 = plt.subplot2grid((4, 2), (3, 0))
        self.chart_creator.create_profit_chart(ax6, stock_metrics)

        ax7 = plt.subplot2grid((4, 2), (3, 1))
        self.chart_creator.create_margin_chart(ax7, stock_metrics)

        # レイアウトを調整
        plt.tight_layout(rect=(0, 0, 1, 0.95))

        # A4サイズで保存
        pdf.savefig(fig, dpi=150)
        plt.close(fig)

    def create_comprehensive_report(self, stock_metrics: StockMetrics) -> Path:
        """単一銘柄のPDFレポートを作成"""
        # ファイル名を設定
        date_short = self.file_manager.get_date_string_short(
            stock_metrics.analysis_date
        )
        filename = f"{stock_metrics.code}_{date_short}_comprehensive_report.pdf"

        try:
            # PDFをメモリ上に作成
            pdf_buffer = io.BytesIO()
            with PdfPages(pdf_buffer) as pdf:
                self._create_report_page(pdf, stock_metrics)

            # save_report()を使ってファイルを保存
            pdf_path = self.file_manager.save_report(
                content=pdf_buffer.getvalue(),
                filename=filename,
                date=stock_metrics.analysis_date,
            )

        except UnicodeEncodeError as e:
            logger.error("PDFエンコードエラー: %s", e)
            raise
        except Exception as e:
            logger.error("PDF生成エラー: %s", e)
            raise

        logger.info("包括的なPDFレポートを作成しました: %s", pdf_path)
        return pdf_path

    def _create_index_page(
        self,
        pdf: PdfPages,
        stock_metrics_list: list[StockMetrics],
        analysis_date: datetime.date,
    ) -> list[tuple[float, float, float, float]]:
        """企業リスト(目次)ページを作成

        Args:
            pdf: PdfPagesオブジェクト
            stock_metrics_list: 銘柄の分析データのリスト
            analysis_date: 分析日

        Returns:
            各企業名セルの位置リスト [(x1, y1, x2, y2), ...] (PDFポイント座標)
        """
        fig = plt.figure(figsize=(8.27, 11.69))

        # タイトル
        fig.suptitle(
            f"複数銘柄分析レポート\nAnalysis Date: {analysis_date}",
            fontsize=16,
            fontweight="bold",
            y=0.95,
        )

        # テーブルで企業リストを表示 (上寄りに配置)
        ax = fig.add_axes((0.1, 0.3, 0.8, 0.6))  # (left, bottom, width, height)
        ax.axis("off")

        # テーブルデータ作成
        table_data = []
        for i, metrics in enumerate(stock_metrics_list, 1):
            table_data.append([str(i), metrics.code, metrics.company_name])

        # テーブル作成 (上寄せ)
        table = ax.table(
            cellText=table_data,
            colLabels=["No.", "証券コード", "企業名"],
            loc="upper center",
            cellLoc="left",
            colWidths=[0.1, 0.2, 0.5],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)

        # ヘッダー行のスタイル
        for j in range(3):
            table[(0, j)].set_facecolor("#4472C4")
            table[(0, j)].set_text_props(color="white", fontweight="bold")

        # 描画してセル位置を取得
        fig.canvas.draw()
        renderer = fig.canvas.renderer  # type: ignore[attr-defined]

        # A4サイズ (ポイント): 595.276 x 841.89
        pdf_width = 595.276
        pdf_height = 841.89
        fig_width, fig_height = fig.get_size_inches()
        dpi = fig.dpi

        link_positions: list[tuple[float, float, float, float]] = []
        for i in range(1, len(stock_metrics_list) + 1):
            # 企業名セル (列インデックス2) の位置を取得
            cell = table[(i, 2)]
            bbox = cell.get_window_extent(renderer)

            # ピクセル座標からPDFポイント座標に変換
            x1 = bbox.x0 / (fig_width * dpi) * pdf_width
            y1 = bbox.y0 / (fig_height * dpi) * pdf_height
            x2 = bbox.x1 / (fig_width * dpi) * pdf_width
            y2 = bbox.y1 / (fig_height * dpi) * pdf_height

            link_positions.append((x1, y1, x2, y2))

        # A4サイズで保存
        pdf.savefig(fig, dpi=150)
        plt.close(fig)

        return link_positions

    def _add_index_links(
        self,
        pdf_bytes: bytes,
        link_positions: list[tuple[float, float, float, float]],
    ) -> bytes:
        """企業リストページに各企業レポートへのリンクを追加

        Args:
            pdf_bytes: 元のPDFデータ
            link_positions: 各企業名セルの位置リスト [(x1, y1, x2, y2), ...]

        Returns:
            リンク追加後のPDFデータ
        """
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()

        # 全ページをコピー
        for page in reader.pages:
            writer.add_page(page)

        # 企業リストページ (0ページ目) にリンクを追加
        for i, (x1, y1, x2, y2) in enumerate(link_positions):
            # リンクアノテーションを作成
            link = Link(
                rect=(x1, y1, x2, y2),
                target_page_index=i + 1,  # 企業リストが0ページ目なので+1
            )
            writer.add_annotation(page_number=0, annotation=link)

        # 結果をバイトとして返す
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        return output_buffer.getvalue()

    def create_multi_company_report(
        self,
        stock_metrics_list: list[StockMetrics],
        output_filename: str | None = None,
    ) -> Path:
        """複数銘柄のレポートを1つのPDFにまとめて出力

        Args:
            stock_metrics_list: 銘柄の分析データのリスト
            output_filename: 出力ファイル名（省略時は日付ベースで自動生成）

        Returns:
            生成されたPDFファイルのパス

        Raises:
            ValueError: stock_metrics_listが空の場合
        """
        if not stock_metrics_list:
            raise ValueError("銘柄リストが空です")

        # 最初の銘柄の分析日を基準にファイル名を生成
        analysis_date = stock_metrics_list[0].analysis_date
        date_short = self.file_manager.get_date_string_short(analysis_date)
        filename = output_filename or f"{date_short}_multi_report.pdf"

        try:
            # PDFをメモリ上に作成
            pdf_buffer = io.BytesIO()
            with PdfPages(pdf_buffer) as pdf:
                # 最初に企業リストページを作成 (リンク位置も取得)
                link_positions = self._create_index_page(
                    pdf, stock_metrics_list, analysis_date
                )

                # 各銘柄のレポートページを作成
                for stock_metrics in stock_metrics_list:
                    self._create_report_page(pdf, stock_metrics)

            # 企業リストページにリンクを追加
            pdf_with_links = self._add_index_links(
                pdf_buffer.getvalue(), link_positions
            )

            # save_report()を使ってファイルを保存
            pdf_path = self.file_manager.save_report(
                content=pdf_with_links,
                filename=filename,
                date=analysis_date,
            )

        except UnicodeEncodeError as e:
            logger.error("PDFエンコードエラー: %s", e)
            raise
        except Exception as e:
            logger.error("PDF生成エラー: %s", e)
            raise

        logger.info(
            "複数銘柄PDFレポートを作成しました（%d銘柄）: %s",
            len(stock_metrics_list),
            pdf_path,
        )
        return pdf_path
