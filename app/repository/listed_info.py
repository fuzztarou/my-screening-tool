"""
上場企業情報ハンドラー

上場企業情報を取得し、CSVファイルとして保存するサービスを提供します。
"""

import logging

import jquantsapi
import pandas as pd

from app.client.jq import create_client
from app.utils.files import FileManager

logger = logging.getLogger(__name__)


class ListedInfoHandler:
    """上場企業情報取得・保存ハンドラークラス"""

    def __init__(
        self,
        client: jquantsapi.Client | None = None,
        file_manager: FileManager | None = None,
    ) -> None:
        """
        初期化

        Args:
            client: J-Quants APIクライアント(省略時は新規作成)
            file_manager: ファイル管理クラス(省略時は新規作成)
        """
        self.client = client or create_client()
        self.file_manager = file_manager or FileManager()

    def create_listed_info_file(self) -> None:
        """上場企業情報ファイル（listed_info.csv）を作成"""
        try:
            date_str = self.file_manager.get_date_string()
            listed_info_path = (
                self.file_manager.base_dir / "temporary" / date_str / "listed_info.csv"
            )

            # 既に存在する場合はスキップ
            if listed_info_path.exists():
                logger.info(
                    "上場企業情報ファイルは既に存在します: %s", listed_info_path
                )
                return

            # APIから上場企業情報を取得
            logger.info("上場企業情報を取得中...")
            listed_info = self.client.get_listed_info()
            df_listed = pd.DataFrame(listed_info)

            # ディレクトリを作成
            listed_info_path.parent.mkdir(parents=True, exist_ok=True)

            # CSVファイルとして保存
            df_listed.to_csv(listed_info_path, index=False)
            logger.info("上場企業情報ファイルを作成しました: %s", listed_info_path)
            logger.info("上場企業数: %d社", len(df_listed))

        except Exception as e:
            logger.exception("上場企業情報ファイル作成中にエラーが発生しました: %s", e)
