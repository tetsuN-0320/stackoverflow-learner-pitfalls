from __future__ import annotations

import html
import re

import pandas as pd
from bs4 import BeautifulSoup

from src.utils.logger import logger


class Cleaner:
    """質問データのHTMLタグ除去・欠損値処理・型変換を担うクラス。"""

    def remove_html(self, text: str) -> str:
        """Stack Overflow 質問本文のHTMLタグを除去してプレーンテキストを返す。"""
        return BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()

    def clean_body(self, text: str) -> str:
        """本文のHTML除去・空白正規化を行う。"""
        text = self.remove_html(text)
        return re.sub(r"\s+", " ", text).strip()

    def clean_questions(self, df: pd.DataFrame) -> pd.DataFrame:
        """質問 DataFrame に対してクリーニングを一括適用する。

        - タイトル欠損・空白のみの行を除去
        - creation_date を UNIX タイムスタンプ → datetime に変換
        - tags 列がリスト型でない場合に変換
        - 重複 question_id を除去
        """
        original = len(df)
        df = df.dropna(subset=["title"]).copy()
        # HTMLエンティティ（&#39; &quot; 等）をデコードしてから空白正規化
        df["title"] = df["title"].apply(html.unescape).str.strip()
        df = df[df["title"].str.len() > 0]

        # creation_date の型変換（UNIXタイムスタンプ → datetime）
        if not pd.api.types.is_datetime64_any_dtype(df["creation_date"]):
            df["creation_date"] = pd.to_datetime(df["creation_date"], unit="s")

        # tags 列が文字列の場合はリストに変換
        if df["tags"].dtype == object and isinstance(df["tags"].dropna().iloc[0], str):
            df["tags"] = df["tags"].str.strip("[]").str.replace("'", "").str.split(", ")

        df = df.drop_duplicates(subset=["question_id"]).reset_index(drop=True)

        dropped = original - len(df)
        if dropped > 0:
            logger.info(f"クリーニング: {dropped}件除去 → {len(df):,}件")
        else:
            logger.info(f"クリーニング完了: {len(df):,}件（除去なし）")

        return df
