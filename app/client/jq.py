"""
J-Quants APIクライアントモジュール

このモジュールはJ-Quants APIを使用して株価データを取得するためのクライアントを提供します。
"""

import jquantsapi


def create_client() -> jquantsapi.Client:
    """
    J-Quants APIクライアントを作成して返します。

    Returns:
        jquantsapi.Client: 設定済みのJ-Quants APIクライアント
    """
    return jquantsapi.Client()
