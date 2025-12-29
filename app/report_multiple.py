"""
複数企業の分析レポートを1つのPDFにまとめて作成するアプリケーション
"""

import datetime
import logging
from pathlib import Path

from .client.jq import create_client
from .services.analyze_quotes import StockDataProcessor
from .repository.quotes import DailyQuotesDataHandler
from .repository.fins import FinsDataHandler
from .repository.listed_info import ListedInfoHandler
from .services.pdf_report_service import PdfReportService
from .utils.stock_code import normalize_stock_code

logger = logging.getLogger(__name__)


def report_multiple_companies(codes: list[str]) -> Path:
    """複数企業の分析レポートを1つのPDFで作成

    Args:
        codes: 銘柄コードのリスト（4桁または5桁）

    Returns:
        生成されたPDFファイルのパス

    Raises:
        ValueError: codesが空の場合、または全ての銘柄コードが無効な場合
    """
    if not codes:
        raise ValueError("銘柄コードリストが空です")

    logger.info("=== 複数企業分析レポート作成開始 ===")
    logger.info("対象銘柄数: %d", len(codes))

    # 銘柄コードを正規化
    normalized_codes: list[str] = []
    for code in codes:
        try:
            normalized = normalize_stock_code(code.strip())
            normalized_codes.append(normalized)
            logger.info("証券コード %s を %s に正規化しました", code, normalized)
        except ValueError as e:
            logger.warning("無効な証券コードをスキップ: %s - %s", code, e)

    if not normalized_codes:
        raise ValueError("有効な銘柄コードがありません")

    # J-Quantsクライアントを作成
    jq_client = create_client()

    # ハンドラーを初期化
    fins_handler = FinsDataHandler(client=jq_client)
    daily_quotes_handler = DailyQuotesDataHandler(client=jq_client)
    listed_info_handler = ListedInfoHandler(client=jq_client)

    # 財務データを取得
    logger.info("財務データを取得中...")
    try:
        fins_handler.prepare_financial_data(normalized_codes=normalized_codes)
    except Exception as e:
        logger.exception("財務データの取得に失敗しました: %s", e)
        raise

    # 上場企業情報を取得
    logger.info("上場企業情報を取得中...")
    try:
        listed_info_handler.prepare_listed_info_data()
    except Exception as e:
        logger.exception("上場企業情報の取得に失敗しました: %s", e)
        raise

    # 株価データを取得
    logger.info("株価データを取得中...")
    try:
        daily_quotes_handler.prepare_daily_quotes_data(normalized_codes=normalized_codes)
    except Exception as e:
        logger.exception("株価データの取得に失敗しました: %s", e)
        raise

    # データ分析
    logger.info("データ分析を開始します...")
    processor = StockDataProcessor()
    stock_metrics_list = processor.process_quotes(
        normalized_codes, datetime.date.today()
    )

    # PDFレポート生成
    logger.info("PDFレポート生成を開始します...")
    pdf_service = PdfReportService()
    pdf_report_path = pdf_service.create_multi_company_report(stock_metrics_list)

    logger.info("=== 複数企業分析レポート作成完了 ===")
    logger.info("対象銘柄数: %d", len(stock_metrics_list))
    logger.info("作成されたファイル: %s", pdf_report_path)

    return pdf_report_path
