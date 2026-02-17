# jq-screening

J-Quants APIを使って日本株の財務・株価データを取得し、PDF分析レポートを自動生成する個人開発ツール。

## 技術スタック

- Python 3.11 / uv（パッケージマネージャー）
- pandas / matplotlib / mplfinance（データ処理・可視化）
- pypdf / Pillow（PDF生成）
- jquants-api-client（J-Quants API）
- mypy（型チェック） / ruff（リント・フォーマット）

## コマンド

```bash
uv run python main.py              # 実行（対話的にモード選択）
uv run ruff check app/ main.py --fix  # リント（自動修正）
uv run ruff format app/ main.py       # フォーマット
uv run mypy app/ main.py              # 型チェック
```

## アーキテクチャ

```
app/
├── client/       # J-Quants APIクライアント生成
├── repository/   # データ取得・CSVキャッシュ
├── types/        # DataFrame型ラッパー（RawFinancialData, RawQuotesData）
├── services/     # 分析ロジック・チャート生成・PDF作成
├── usecase/      # ワークフロー（単一/複数銘柄レポート）
├── constants/    # カラム定義
└── utils/        # 日付・ファイル・銘柄コードのユーティリティ
config/           # 環境変数・対象銘柄設定
data/
├── outputs/      # PDF出力（YYMMDD/）
└── temp/         # APIキャッシュCSV（YYMMDD/銘柄コード/）
```

レイヤー構成: **Client → Repository → Service → UseCase**
新機能追加時はこのレイヤーに従うこと。

## コーディング規約

- 型ヒント必須（mypy strict: `disallow_untyped_defs = true`）
- docstringは日本語
- ruff: line-length=88, double quotes, space indent
- コミットメッセージ: `feat:/fix:/refactor:/docs:` + 日本語の簡潔な説明

## 環境変数（.env）

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `LOG_LEVEL` | ログレベル | INFO |
| `DATA_YEARS_AGO` | 過去データ取得年数 | 5 |
| `SCREENING_PSR_MIN/MAX` | PSRスクリーニング閾値 | 0.0 / 2.0 |
| `SCREENING_ROE_MIN/MAX` | ROEスクリーニング閾値 | 1.0 / 100.0 |

## 認証

J-Quants APIの認証情報は `jquants-api.toml` に設定。
