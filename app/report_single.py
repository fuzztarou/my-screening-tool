"""
特定の企業の分析レポートを作成するアプリケーション
"""

import datetime
import logging

from .client.jq import create_client
from .services.analyze_quotes import StockDataProcessor
from .services.chart_service import ChartService
from .services.daily_quotes import DailyQuotesDataHandler
from .services.fins import FinsDataHandler
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
        fins_handler.fetch_and_save_financial_data(stock_codes=[code])
        logger.info("証券コード %s の財務データを取得・保存しました。", code)
    except Exception as e:
        logger.exception("証券コード %s のデータ取得に失敗しました: %s", code, e)
        return

    # 株価データを取得
    try:
        api_codes = daily_quotes_handler.fetch_and_save_daily_quotes(stock_codes=[code])
        logger.info("証券コード %s の株価データを取得・保存しました。", code)
        logger.info("APIから取得した企業コード: %s", api_codes)
    except Exception as e:
        logger.exception("証券コード %s の株価データ取得に失敗しました: %s", code, e)
        return

    # データ分析とチャート作成
    try:
        # 分析対象日を設定（今日の日付）
        analysis_date = datetime.date.today()
        logger.info("分析対象日: %s", analysis_date)

        # StockDataProcessorを初期化
        processor = StockDataProcessor()
        logger.info("StockDataProcessorを初期化しました。")

        # 財務データを読み込み
        processor.load_fins_data(analysis_date)
        logger.info("財務データを読み込みました。")

        # 株価データを分析 - APIから取得したコードを使用
        codes_to_process = api_codes if api_codes else [code]
        stock_metrics = processor.process_quotes(codes_to_process, analysis_date)
        logger.info("証券コード %s のデータ分析が完了しました。", code)
        logger.info("企業名: %s", stock_metrics[0].company_name)

        # ChartServiceを初期化
        chart_service = ChartService()
        logger.info("ChartServiceを初期化しました。")

        # 各種チャートを作成
        logger.info("チャート作成を開始します...")

        # 株価チャート
        price_chart_path = chart_service.create_price_chart(stock_metrics[0])
        logger.info("株価チャートを作成しました: %s", price_chart_path)

        # 指標チャート
        indicators_chart_path = chart_service.create_indicators_chart(stock_metrics[0])
        logger.info("指標チャートを作成しました: %s", indicators_chart_path)

        # 出来高チャート
        volume_chart_path = chart_service.create_volume_chart(stock_metrics[0])
        logger.info("出来高チャートを作成しました: %s", volume_chart_path)

        # 利益チャート
        profit_chart_path = chart_service.create_profit_chart(stock_metrics[0])
        if profit_chart_path:
            logger.info("利益チャートを作成しました: %s", profit_chart_path)
        else:
            logger.warning("利益チャートの作成をスキップしました（データ不足）")

        # PDFレポート生成
        pdf_service = PdfReportService()
        pdf_report_path = pdf_service.create_comprehensive_report(stock_metrics[0])
        logger.info("包括的なPDFレポートを作成しました: %s", pdf_report_path)

        logger.info("=== 分析レポート作成完了 ===")
        logger.info("証券コード: %s", code)
        logger.info("企業名: %s", stock_metrics[0].company_name)
        logger.info("分析日: %s", analysis_date)
        logger.info("作成されたファイル:")
        logger.info("  - 株価チャート: %s", price_chart_path)
        logger.info("  - 指標チャート: %s", indicators_chart_path)
        logger.info("  - 出来高チャート: %s", volume_chart_path)
        if profit_chart_path:
            logger.info("  - 利益チャート: %s", profit_chart_path)
        logger.info("  - 包括的PDFレポート: %s", pdf_report_path)

    except Exception as e:
        logger.exception("データ分析またはチャート作成に失敗しました: %s", e)
        return


if __name__ == "__main__":
    report_single_company()
