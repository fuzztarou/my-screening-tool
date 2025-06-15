import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    _instance = None

    MY_EMAIL: Optional[str] = None
    JPX_PASSWORD: Optional[str] = None

    def __new__(cls):
        # 既にインスタンスが存在する場合はそれを返す（早期リターン）
        if cls._instance is not None:
            return cls._instance

        # 新しいインスタンスを作成
        cls._instance = super().__new__(cls)

        # 環境変数を読み込む
        cls._instance.MY_EMAIL = os.getenv("MY_EMAIL")
        if cls._instance.MY_EMAIL is None:
            print("警告: MY_EMAIL 環境変数が設定されていません")

        cls._instance.JPX_PASSWORD = os.getenv("JPX_PASSWORD")
        if cls._instance.JPX_PASSWORD is None:
            print("警告: JPX_PASSWORD 環境変数が設定されていません")

        return cls._instance
