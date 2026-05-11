from __future__ import annotations

import re

import nltk

from src.preprocessing.stopwords import DOMAIN_STOPWORDS


class Tokenizer:
    """英語テキストのトークナイズとストップワード除去を担うクラス。

    コードスニペット内の識別子は通常の英単語と扱いが異なるため、
    バッククォートで囲まれた部分を先に除去してからトークナイズする。
    """

    def __init__(self) -> None:
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
        self._stopwords = (
            set(nltk.corpus.stopwords.words("english")) | DOMAIN_STOPWORDS
        )

    def tokenize(self, text: str) -> list[str]:
        """テキストをトークンのリストに変換する。"""
        text = re.sub(r"`[^`]+`", " ", text)
        tokens = nltk.word_tokenize(text.lower())
        return [t for t in tokens if t.isalpha() and t not in self._stopwords]
