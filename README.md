# my-screening-tool

J-Quants APIを使って日本株の財務・株価データを取得し、PDF分析レポートを自動生成する個人開発ツール。

証券コードを入力するだけで、財務指標の算出・チャート生成・PDF出力までを一気通貫で実行する。複数銘柄をまとめたレポートでは、インデックスページから各企業ページへのリンクナビゲーションも備える。

## 主な特徴

- **18種の財務指標を自動算出** — PER/PBR/PSR/ROE/ROA/PEG/マージン/時価総額に加え、自己資本比率ベースのディスカウント率とPBRベースのリスク評価率から理論株価を独自算出
- **8種のチャートを1ページに集約** — 株価・出来高、キャッシュフロー、バリュエーション指標、売上・利益推移、マージン推移を一覧可能なレイアウトで生成
- **複数銘柄レポート** — インデックスページ付きの統合PDFを生成し、pypdfによるページ内リンクで各企業に直接ジャンプ可能
- **CSVキャッシュ** — 同日のAPI呼び出しを自動スキップし、不要なリクエストを削減

## 技術スタック

| カテゴリ             | 技術                    |
| -------------------- | ----------------------- |
| 言語                 | Python 3.11+            |
| パッケージ管理       | uv                      |
| データ処理           | pandas                  |
| 可視化               | matplotlib / mplfinance |
| PDF生成              | pypdf / Pillow          |
| API                  | jquants-api-client      |
| 型チェック           | mypy（strict）          |
| リント・フォーマット | ruff                    |

## アーキテクチャ

レイヤードアーキテクチャを採用し、各層の責務を明確に分離している。

```
Client → Repository → Types → Service → UseCase
```

| レイヤー       | 責務                                            |
| -------------- | ----------------------------------------------- |
| **Client**     | J-Quants APIクライアントの生成                  |
| **Repository** | APIからのデータ取得とCSVキャッシュ管理          |
| **Types**      | 生DataFrameのラップ、バリデーション、型変換     |
| **Service**    | 指標計算、チャート生成、PDF出力                 |
| **UseCase**    | Repository → Service を組み合わせたワークフロー |

上位レイヤーは下位レイヤーにのみ依存する。

## セットアップ

### 前提条件

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- [J-Quants API](https://jpx-jquants.com/#jquants-api) のアカウント

### インストール

```bash
git clone https://github.com/<your-username>/jq-screening.git
cd jq-screening
uv sync
```

### 認証情報

J-Quants APIの認証情報を `jquants-api.toml` に設定する。
詳細は [jquants-api-client-python の設定](https://github.com/J-Quants/jquants-api-client-python?tab=readme-ov-file#%E8%A8%AD%E5%AE%9A) を参照。

## 使い方

### 単一銘柄レポート

```bash
uv run python main.py
```

モード選択で「1」を選択し、証券コードを入力する。

### 複数銘柄レポート

1. `config/target_codes.txt` を作成し、対象銘柄コードを記載する:

```
# 対象銘柄コード（1行1銘柄、#でコメント）
1301
7203
9984
```

2. 実行してモード選択で「2」を選択:

```bash
uv run python main.py
```

複数銘柄のレポートが1つのPDFにまとめて出力される。

## 環境変数

`.env` ファイルで以下の設定が可能:

| 変数名              | デフォルト | 説明                       |
| ------------------- | ---------- | -------------------------- |
| `LOG_LEVEL`         | `INFO`     | ログレベル                 |
| `DATA_YEARS_AGO`    | `5`        | 過去データ取得年数         |
| `SCREENING_PSR_MIN` | `0.0`      | PSRスクリーニング下限      |
| `SCREENING_PSR_MAX` | `2.0`      | PSRスクリーニング上限      |
| `SCREENING_ROE_MIN` | `1.0`      | ROEスクリーニング下限（%） |
| `SCREENING_ROE_MAX` | `100.0`    | ROEスクリーニング上限（%） |

## 出力ディレクトリ構成

```
data/
├── outputs/            # 生成されたPDFレポート
│   └── 251220/
│       └── 60880_251220_comprehensive_report.pdf
└── temp/               # APIレスポンスのCSVキャッシュ
    └── 251220/
        ├── 60880/
        │   ├── 60880_251220_fins.csv
        │   └── 60880_251220_quotes.csv
        ├── fins_targets.csv
        └── listed_info.csv
```
