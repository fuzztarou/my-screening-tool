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

```bash
python main.py
```

証券コードの入力を求められるので、4桁または5桁のコードを入力する。

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
