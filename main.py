"""
J-Quants APIを使用した株価データ取得のメインアプリケーション
"""
from datetime import datetime
from dateutil import tz
from client.client import create_client


def main() -> None:
    """メイン実行関数"""
    print("Hello from jq-screening!")

    # クライアントを作成
    client = create_client()
    print("J-Quants APIクライアントを作成しました。")

    # 株価データを取得
    try:
        df = client.get_price_range(
            start_dt=datetime(2022, 7, 25, tzinfo=tz.gettz("Asia/Tokyo")),
            end_dt=datetime(2022, 7, 26, tzinfo=tz.gettz("Asia/Tokyo")),
        )
        print("株価データを取得しました:")
        print(df)
    except Exception as e:
        print(f"データ取得中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
