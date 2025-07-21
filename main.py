"""
J-Quants APIを使用した株価データ取得のメインアプリケーション
"""

import logging

from app import report_single as single
from config.config import config

logger = logging.getLogger(__name__)


def main() -> None:
    """メイン実行関数"""
    # ログ設定を初期化
    config.set_config()

    logger.info("Hello from jq-screening!")

    # 特定の銘柄のレポートを作成
    single.report_single_company()


if __name__ == "__main__":
    main()
