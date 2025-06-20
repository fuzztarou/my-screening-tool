"""
J-Quants APIクライアントモジュール

このモジュールはJ-Quants APIを使用して株価データを取得するためのクライアントを提供します。
"""
import jquantsapi
from config.config import Config


def create_client() -> jquantsapi.Client:
    """
    J-Quants APIクライアントを作成して返します。

    Returns:
        jquantsapi.Client: 設定済みのJ-Quants APIクライアント
    """
    config = Config()
    return jquantsapi.Client(mail_address=config.MY_EMAIL, password=config.JPX_PASSWORD)
