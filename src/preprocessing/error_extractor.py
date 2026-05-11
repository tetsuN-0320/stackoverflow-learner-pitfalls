from __future__ import annotations

import re


# Python / JavaScript / Java の代表的なエラーパターン
_ERROR_PATTERNS = [
    r"[A-Z][a-zA-Z]+Error",
    r"[A-Z][a-zA-Z]+Exception",
    r"TypeError",
    r"ValueError",
    r"AttributeError",
    r"ImportError",
    r"KeyError",
    r"IndexError",
    r"NullPointerException",
    r"ReferenceError",
    r"SyntaxError",
]

_ERROR_RE = re.compile("|".join(_ERROR_PATTERNS))


class ErrorExtractor:
    """質問本文からエラーメッセージパターンを抽出するクラス。"""

    def extract(self, text: str) -> list[str]:
        """テキスト中に含まれるエラークラス名をリストで返す。"""
        return _ERROR_RE.findall(text)
