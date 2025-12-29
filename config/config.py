"""
アプリケーション設定モジュール
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()


class Config:
    """アプリケーション設定クラス"""

    def __init__(self) -> None:
        # ログ設定
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(levelname)s: %(message)s")

        # 株価データ設定
        self.DATA_YEARS_AGO: int = int(os.getenv("DATA_YEARS_AGO", "5"))

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

# 対象銘柄コード設定ファイルのパス
TARGET_CODES_FILE = Path("config/target_codes.txt")


def load_target_codes(file_path: Path = TARGET_CODES_FILE) -> list[str]:
    """設定ファイルから対象銘柄コードを読み込む

    Args:
        file_path: 設定ファイルのパス

    Returns:
        銘柄コードのリスト

    Raises:
        FileNotFoundError: 設定ファイルが存在しない場合
    """
    if not file_path.exists():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {file_path}")

    codes: list[str] = []
    with file_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 空行とコメント行をスキップ
            if line and not line.startswith("#"):
                codes.append(line)

    return codes
