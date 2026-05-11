from __future__ import annotations

import pandas as pd
from bs4 import BeautifulSoup


class Cleaner:
    """質問データのHTMLタグ除去・欠損値処理・型変換を担うクラス。"""

    def remove_html(self, text: str) -> str:
        """Stack Overflow 質問本文のHTMLタグを除去してプレーンテキストを返す。"""
        return BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()

    def clean_questions(self, df: pd.DataFrame) -> pd.DataFrame:
        """質問DataFrameに対してHTML除去・欠損除去・型変換を適用する。"""
        raise NotImplementedError("Day 4 で実装")
