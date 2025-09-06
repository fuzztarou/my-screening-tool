"""
証券コード関連のユーティリティ関数
"""

from typing import List


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
        >>> normalize_stock_code("215a")
        "215A0"
    """
    code = str(input_code).strip().upper()  # 大文字に変換

    if len(code) == 4:
        # 4桁の場合: 末尾に0を追加
        return code + "0"
    elif len(code) == 5:
        # 5桁の場合: そのまま使用
        return code
    else:
        raise ValueError(f"無効な証券コード: {code} (長さ: {len(code)}桁)")


def normalize_stock_codes(input_codes: List[str]) -> List[str]:
    """
    証券コードのリストを5桁に正規化

    Args:
        input_codes: 入力された証券コードのリスト

    Returns:
        List[str]: 5桁に正規化された証券コードのリスト

    Raises:
        ValueError: 無効な証券コードが含まれている場合

    Examples:
        >>> normalize_stock_codes(["1301", "13010", "25935"])
        ["13010", "13010", "25935"]
        >>> normalize_stock_codes(["1301", "215a", "9999"])
        ["13010", "215A0", "99990"]
        >>> normalize_stock_codes([])
        []
    """
    if not input_codes:
        return []

    normalized_codes = []
    for code in input_codes:
        try:
            normalized_code = normalize_stock_code(code)
            normalized_codes.append(normalized_code)
        except ValueError as e:
            # エラーメッセージにリスト内の位置情報を追加
            index = input_codes.index(code)
            raise ValueError(
                f"リスト内のインデックス: {index} 値: {code} でエラー: {str(e)}"
            ) from e

    return normalized_codes
