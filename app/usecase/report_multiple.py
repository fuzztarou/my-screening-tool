"""
設定ファイルから複数企業レポートを作成
"""

import datetime
import logging
from pathlib import Path

from config.config import load_target_codes

from app.client.jq import create_client
from app.services.analyze_quotes import StockDataProcessor
from app.repository.quotes import DailyQuotesDataHandler
from app.repository.fins import FinsDataHandler
from app.repository.listed_info import ListedInfoHandler
from app.services.pdf_report_service import PdfReportService
from app.utils.stock_code import normalize_stock_codes

logger = logging.getLogger(__name__)


def report_from_config() -> Path:
    """設定ファイルから銘柄コードを読み込んでレポートを作成

    Returns:
        生成されたPDFファイルのパス

    Raises:
        FileNotFoundError: 設定ファイルが存在しない場合
        ValueError: 設定ファイルに有効な銘柄コードがない場合
    """
    codes = load_target_codes()
    if not codes:
        raise ValueError("設定ファイルに銘柄コードがありません")
    logger.info("設定ファイルから銘柄コードを読み込みました: %s", codes)

    logger.info("=== 複数企業分析レポート作成開始 ===")
    logger.info("対象銘柄数: %d", len(codes))

    # 銘柄コードを正規化
    normalized_codes = normalize_stock_codes(codes)
    logger.info("銘柄コードを正規化しました: %s", normalized_codes)

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
