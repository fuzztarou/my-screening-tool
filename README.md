## データ取得先
[J-Quants API](https://jpx-jquants.com/#jquants-api)

## API クライアント
[jquants-api-client-python](https://github.com/J-Quants/jquants-api-client-python)

## 認証情報
- `jquants-api.toml` に設定しておく
- [参照](https://github.com/J-Quants/jquants-api-client-python?tab=readme-ov-file#%E8%A8%AD%E5%AE%9A)

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
