# my-screening-tool

J-Quants APIを使用して日本株の財務・株価データを取得し、分析レポート（PDF）を自動生成するツール。

## 機能

- 証券コードを入力して企業データを取得
- 財務データ（売上、営業利益、当期利益、マージン等）の分析
- 株価・出来高チャートの生成
- バリュエーション指標（PER、PBR、ROE、ROA、PSR等）の可視化
- PDFレポートの自動生成

## セットアップ

### データ取得先
[J-Quants API](https://jpx-jquants.com/#jquants-api)

### API クライアント
[jquants-api-client-python](https://github.com/J-Quants/jquants-api-client-python)

### 認証情報
- `jquants-api.toml` に設定しておく
- [参照](https://github.com/J-Quants/jquants-api-client-python?tab=readme-ov-file#%E8%A8%AD%E5%AE%9A)

## 使い方

### 単一銘柄レポート

```bash
python main.py
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
python main.py
```

複数銘柄のレポートが1つのPDFファイルにまとめて出力される。

## 出力データのディレクトリ構成

```
data/
├── outputs/            # 出力データ（削除禁止）
│   └── 251220/
│       └── 60880_251220_comprehensive_report.pdf
└── temp/               # 一時データ（削除対象）
    └── 251220/
        ├── 60880/
        │   ├── 60880_251220_fins.csv
        │   └── 60880_251220_quotes.csv
        ├── fins_targets.csv
        └── listed_info.csv
```
