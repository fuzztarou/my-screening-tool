"""
特定の企業の分析レポートを作成するアプリケーション
"""
from .client.client import create_client


def report_specified() -> None:
    """特定の企業の分析レポートを作成する関数"""
    print("Hello from report_specified!")

    # クライアントを作成
    client = create_client()
    print("J-Quants APIクライアントを作成しました。")

    # 株価データを取得
    try:
        df = client.get_listed_info(code="", date_yyyymmdd="")
        print("財務データを取得しました:")
        print(df)
    except Exception as e:
        print(f"データ取得中にエラーが発生しました: {e}")


if __name__ == "__main__":
    report_specified()
