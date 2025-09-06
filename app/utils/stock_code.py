"""
証券コード関連のユーティリティ関数
"""


def normalize_stock_code(input_code: str) -> str:
    """
    証券コードを5桁に正規化

    Args:
        input_code: 入力された証券コード（文字列）

    Returns:
        str: 5桁に正規化された証券コード

    Raises:
        ValueError: 無効な証券コードの場合

    Examples:
        >>> normalize_stock_code("1301")
        "13010"
        >>> normalize_stock_code("13010")
        "13010"
        >>> normalize_stock_code("25935")
        "25935"
    """
    code = str(input_code).strip()

    if len(code) == 4:
        # 4桁の場合: 末尾に0を追加
        return code + "0"
    elif len(code) == 5:
        # 5桁の場合: そのまま使用
        return code
    else:
        raise ValueError(f"無効な証券コード: {code} (長さ: {len(code)}桁)")
