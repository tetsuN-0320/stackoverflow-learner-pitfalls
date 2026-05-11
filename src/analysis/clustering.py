from __future__ import annotations

import numpy as np
import pandas as pd


class QuestionClusterer:
    """ミクロ層: 質問本文のトピッククラスタリングを担うクラス。

    TF-IDF でベクトル化し、HDBSCANでクラスタを自動決定する。
    クラスタ数を事前指定不要なのが HDBSCAN の強み。
    Day 7 で実装する。
    """

    def vectorize(self, texts: list[str]) -> np.ndarray:
        """TF-IDFでテキストをベクトル化する。"""
        raise NotImplementedError("Day 7 で実装")

    def cluster(self, vectors: np.ndarray) -> np.ndarray:
        """HDBSCANでクラスタラベルを付与する。-1はノイズ点。"""
        raise NotImplementedError("Day 7 で実装")

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """テキスト列にクラスタIDを付与したDataFrameを返す。"""
        raise NotImplementedError("Day 7 で実装")
