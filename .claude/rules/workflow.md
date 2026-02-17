# 開発ワークフロー

- コード変更後は必ず以下を順番に実行する:
  1. `uv run ruff check app/ main.py --fix`
  2. `uv run ruff format app/ main.py`
  3. `uv run mypy app/ main.py`
- 依存追加は `uv add <package>`（dev用は `uv add --group dev <package>`）
- `.env`, `data/`, `config/target_codes.txt` はgitignore対象。コミットしないこと
- コミットメッセージ: `feat:/fix:/refactor:/docs:` + 日本語の簡潔な説明
