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

logger = logging.getLogger(__name__)


def report_single_company() -> None:
    """特定の企業の分析レポートを作成する関数"""

    logger.info("Hello from report_single_company!")

    # クライアントを作成
    client = create_client()
    logger.info("J-Quants APIクライアントを作成しました。")

    # FinsDataHandlerを初期化
    fins_handler = FinsDataHandler(client=client)
    logger.info("FinsDataHandlerを初期化しました。")

    # DailyQuotesDataHandlerを初期化
    daily_quotes_handler = DailyQuotesDataHandler(client=client)
    logger.info("DailyQuotesDataHandlerを初期化しました。")

    # ユーザーからコードの入力
    code = input("企業の証券コードを入力してください: ").strip()

    # 財務データを取得
    try:
        fins_handler.fetch_and_save_financial_data(input_codes=[code])
        logger.info("証券コード %s の財務データを取得・保存しました。", code)
    except Exception as e:
        logger.exception("証券コード %s のデータ取得に失敗しました: %s", code, e)
        return

    # 株価データを取得
    try:
        api_codes = daily_quotes_handler.fetch_and_save_daily_quotes(stock_codes=[code])
        logger.info("証券コード %s の株価データを取得・保存しました。", code)
    except Exception as e:
        logger.exception("証券コード %s の株価データ取得に失敗しました: %s", code, e)
        return

    # データ分析とチャート作成
    try:
        # StockDataProcessorを初期化
        processor = StockDataProcessor()
        logger.info("StockDataProcessorを初期化しました。")

        stock_metrics = processor.process_quotes(api_codes, datetime.date.today())
        logger.info("証券コード %s のデータ分析が完了しました。", code)

        # PDFレポート生成
        pdf_service = PdfReportService()
        pdf_report_path = pdf_service.create_comprehensive_report(stock_metrics[0])
        logger.info("包括的なPDFレポートを作成しました: %s", pdf_report_path)

        logger.info("=== 分析レポート作成完了 ===")
        logger.info("証券コード: %s  企業名: %s", code, stock_metrics[0].company_name)
        logger.info("作成されたファイル: %s", pdf_report_path)

    except Exception as e:
        logger.exception("データ分析またはチャート作成に失敗しました: %s", e)
        return


if __name__ == "__main__":
    report_single_company()
