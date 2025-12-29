"""
設定ファイルから複数企業レポートを作成するラッパー
"""

import logging
from pathlib import Path

from config.config import load_target_codes

from .services.report_generator import generate_multi_report

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
    return generate_multi_report(codes)
