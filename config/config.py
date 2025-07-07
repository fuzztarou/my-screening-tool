"""
アプリケーション設定モジュール
"""

import logging
import os

from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()


class Config:
    """アプリケーション設定クラス"""

    def __init__(self) -> None:
        # ログ設定
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(levelname)s: %(message)s")

    def set_config(self) -> None:
        """アプリケーション設定を初期化"""
        self.setup_logging()

    def setup_logging(self) -> None:
        """ログ設定を初期化"""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL.upper()),
            format=self.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),  # コンソール出力
            ],
        )

        # ログ設定完了メッセージ
        logger = logging.getLogger(__name__)
        logger.info(f"ログ設定が完了しました (レベル: {self.LOG_LEVEL})")


# グローバル設定インスタンス
config = Config()
