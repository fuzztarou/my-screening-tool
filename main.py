"""
J-Quants APIを使用した株価データ取得のメインアプリケーション
"""
from app.report_specified import report_specified


def main() -> None:
    """メイン実行関数"""
    print("Hello from jq-screening!")

    # 特定の銘柄のレポートを作成
    report_specified()

if __name__ == "__main__":
    main()
