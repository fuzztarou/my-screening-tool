"""
特定の企業の分析レポートを作成するアプリケーション
"""

import logging

from .client.jq import create_client
from .services.fins import FinsDataHandler

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

    # ユーザーからコードの入力
    code = input("企業の証券コードを入力してください: ").strip()

    # 会社データを取得
    try:
        fins_handler.fetch_and_save_financial_data(stock_codes=[code])
        logger.info("証券コード %s の財務データを取得・保存しました。", code)
    except Exception as e:
        logger.exception("証券コード %s のデータ取得に失敗しました: %s", code, e)
        return


if __name__ == "__main__":
    report_single_company()
