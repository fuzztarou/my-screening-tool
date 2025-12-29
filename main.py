"""
J-Quants APIを使用した株価データ取得のメインアプリケーション
"""

import logging

from app import report_single as single
from app import report_multiple as multiple
from config.config import config

logger = logging.getLogger(__name__)


def main() -> None:
    """メイン実行関数"""
    # ログ設定を初期化
    config.set_config()

    logger.info("Hello from jq-screening!")

    # モード選択
    print("\n=== レポート作成モード ===")
    print("1. 単一銘柄レポート")
    print("2. 複数銘柄レポート")
    print()

    mode = input("モードを選択してください (1/2): ").strip()

    if mode == "1":
        single.report_single_company()
    elif mode == "2":
        multiple.report_from_config()
    else:
        print("無効な選択です。1または2を入力してください。")


if __name__ == "__main__":
    main()
