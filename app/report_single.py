"""
特定の企業の分析レポートを作成するアプリケーション
"""

import datetime
import logging

from .client.jq import create_client
from .services.analyze_quotes import StockDataProcessor
from .repository.quotes import DailyQuotesDataHandler
from .repository.fins import FinsDataHandler
from .services.pdf_report_service import PdfReportService
from .utils.stock_code import normalize_stock_code

logger = logging.getLogger(__name__)


def report_single_company() -> None:
    """特定の企業の分析レポートを作成する関数"""

    logger.info("=== 企業分析レポート作成開始 ===")

    # クライアントを作成
    client = create_client()

    # ハンドラーを初期化
    fins_handler = FinsDataHandler(client=client)
    daily_quotes_handler = DailyQuotesDataHandler(client=client)

    # ユーザーからコードの入力
    input_code = input("企業の証券コードを入力してください: ").strip()

    # 入力されたコードを正規化
    try:
        normalized_code = normalize_stock_code(input_code)
        logger.info("証券コード %s を %s に正規化しました", input_code, normalized_code)
    except ValueError as e:
        logger.error("無効な証券コード: %s", e)
        return

    # 財務データを取得
    try:
        fins_handler.prepare_financial_data(normalized_codes=[normalized_code])
    except Exception as e:
        logger.exception(
            "証券コード %s のデータ取得に失敗しました: %s", normalized_code, e
        )
        return

    # 株価データを取得
    try:
        normalized_codes = daily_quotes_handler.fetch_and_save_daily_quotes(
            normalized_codes=[normalized_code]
        )
    except Exception as e:
        logger.exception(
            "証券コード %s の株価データ取得に失敗しました: %s", normalized_code, e
        )
        return

    # データ分析とレポート作成
    try:
        logger.info("データ分析を開始します...")
        processor = StockDataProcessor()
        stock_metrics = processor.process_quotes(
            normalized_codes, datetime.date.today()
        )

        logger.info("PDFレポート生成を開始します...")
        pdf_service = PdfReportService()
        pdf_report_path = pdf_service.create_comprehensive_report(stock_metrics[0])

        logger.info("=== 分析レポート作成完了 ===")
        logger.info(
            "証券コード: %s  企業名: %s", normalized_code, stock_metrics[0].company_name
        )
        logger.info("作成されたファイル: %s", pdf_report_path)

    except Exception as e:
        logger.exception("データ分析またはチャート作成に失敗しました: %s", e)
        return


if __name__ == "__main__":
    report_single_company()
