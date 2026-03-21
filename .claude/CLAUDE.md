# jq-screening

J-Quants APIを使って日本株の財務・株価データを取得し、PDF分析レポートを自動生成する個人開発ツール。

## 技術スタック

- Python 3.11 / uv（パッケージマネージャー）
- pandas / matplotlib / mplfinance（データ処理・可視化）
- pypdf / Pillow（PDF生成）
- jquants-api-client（J-Quants API）
- mypy（型チェック） / ruff（リント・フォーマット）

## 実装の流れ

```
調査 → Plan → 実装 → lint/型チェック → レビュー
```

| ステップ | 内容 |
|----------|------|
| 1. 調査 | CLAUDE.md・既存コードを確認、不明点を質問 |
| 2. Plan | planモードで実装計画、ユーザー承認を得る |
| 3. 実装 | コード実装 |
| 4. チェック | ruff + mypy で品質確認 |
| 5. レビュー | コードレビュー |

## 実装前ルール（必須）

**実装タスクではplanモードを使用すること。**

1. まずCLAUDE.mdと関連コードを読む
2. planモードで実装計画を立てる
3. ユーザーの承認を得てから実装開始

**不明点は選択肢とメリデメを提示し、自分の意見を述べること。**

## コマンド

```bash
# 実行（対話的にモード選択）
uv run python main.py

# lint・フォーマット・型チェック（実装後に必ず実行）
uv run ruff check app/ main.py --fix
uv run ruff format app/ main.py
uv run mypy app/ main.py

# 依存追加
uv add <package>
uv add --group dev <package>
```

## ルール

### 必須
- **mainブランチに直接コミットしない。必ずブランチを切ってPRで統合する**
- シークレット（APIキー等）をハードコードしない（`jquants-api.toml` で管理）
- `.env`, `data/`, `config/target_codes.txt` はgitignore対象。コミットしないこと

### ブランチ運用
- ブランチ名: `feat/<機能名>`, `fix/<修正内容>`, `refactor/<内容>`, `docs/<ドキュメント>`
- コミットメッセージ: `feat:/fix:/refactor:/docs:` + 日本語の簡潔な説明
- PRマージ後にブランチ削除

### 規約
- 型ヒント必須（mypy strict: `disallow_untyped_defs = true`）
- docstringは日本語で書く
- ruff: line-length=88, double quotes, space indent
- 既存コードのパターンに合わせて書くこと（まず関連ファイルを読んでから実装する）
- 新機能追加時はレイヤー構成（Client → Repository → Types → Service → UseCase）に従う
- 上位レイヤーは下位レイヤーにのみ依存する

### データ安全性
- J-Quants APIの認証情報は `jquants-api.toml` に設定（gitignore対象）
- CSVキャッシュは `data/temp/YYMMDD/銘柄コード/` に保存（gitignore対象）
- 生成PDFは `data/outputs/YYMMDD/` に出力（gitignore対象）

## アーキテクチャ

レイヤー構成: **Client → Repository → Types → Service → UseCase**

### `app/client/` — APIクライアント生成

J-Quants APIクライアントのファクトリ。`create_client()` でインスタンスを返すだけ。
認証情報は `jquants-api.toml` から自動読み込み。

### `app/repository/` — データ取得・キャッシュ

APIからデータを取得し、`data/temp/YYMMDD/銘柄コード/` にCSVキャッシュとして保存。
既にCSVが存在すればAPI呼び出しをスキップする。

- `FinsDataHandler` — 財務データ（PL/BS/CF）の取得・統合ファイル作成
- `DailyQuotesDataHandler` — 株価データ（OHLCV）の取得
- `ListedInfoHandler` — 上場企業情報の取得

### `app/types/` — DataFrame型ラッパー

生DataFrameをラップしてバリデーション・型変換を行う。
`from_csv()` で読み込むとカラム存在確認＋数値変換が自動実行される。

- `RawFinancialData` — 財務データ用
- `RawQuotesData` — 株価データ用

### `app/services/` — 分析・可視化・PDF生成

ビジネスロジックの中核。

- `StockDataProcessor` — 財務＋株価データのマージ、指標計算のオーケストレーション
- `IndicatorCalculator` — PER/PBR/PSR/ROE/ROA/PEG/マージン/時価総額/理論株価など全指標を計算
- `ChartCreator` — matplotlib で8種類のチャートを生成
- `PdfReportService` — チャートをA4ページに配置してPDF出力。複数銘柄レポートではインデックスページ＋ページ間リンクも生成
- `Plotter` — matplotlib の低レベルユーティリティ

### `app/usecase/` — ワークフロー

エントリポイントから呼ばれる処理フロー。Repository → Service を順番に呼び出す。

- `report_single_company(code)` — 単一銘柄のレポート作成
- `report_from_config()` — `config/target_codes.txt` から複数銘柄レポート作成

### `app/constants/` — カラム定義

APIから取得するデータのカラム名リスト（抽出対象・数値変換対象）。

### `app/utils/` — ユーティリティ

- `FileManager` — 日付ベースのパス構築（`data/temp/YYMMDD/`, `data/outputs/YYMMDD/`）
- `dates` — 日付フォーマット（ISO/YYMMDD）、JST現在日取得
- `stock_code` — 証券コードの正規化（4桁→5桁変換）

### `config/` — 設定

- `config.py` — 環境変数読み込み、ログ設定
- `target_codes.txt` — 対象銘柄コード一覧（`#` でコメント、gitignore対象）

### `data/` — データ（gitignore対象）

- `outputs/YYMMDD/` — 生成されたPDFレポート
- `temp/YYMMDD/銘柄コード/` — APIレスポンスのCSVキャッシュ

## 環境変数（.env）

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `LOG_LEVEL` | ログレベル | INFO |
| `DATA_YEARS_AGO` | 過去データ取得年数 | 5 |
| `SCREENING_PSR_MIN/MAX` | PSRスクリーニング閾値 | 0.0 / 2.0 |
| `SCREENING_ROE_MIN/MAX` | ROEスクリーニング閾値 | 1.0 / 100.0 |

## 認証

J-Quants APIの認証情報は `jquants-api.toml` に設定。
