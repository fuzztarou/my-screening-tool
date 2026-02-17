---
name: lint
description: リント、フォーマット、型チェックを実行する
allowed-tools: Bash
---

以下のコマンドを順番に実行してください:

```bash
uv run ruff check app/ main.py --fix
uv run ruff format app/ main.py
uv run mypy app/ main.py
```

各ステップの結果を簡潔に報告してください。エラーがあれば修正案を提示してください。
