from __future__ import annotations

import pandas as pd


class PitfallExtractor:
    """ミクロ層: クラスタリング結果から「つまづきパターン」を命名・ランク付けするクラス。

    各クラスタの代表語（TF-IDFスコア上位語）を抽出して、
    人間が読めるトピック名を付与する。Day 7 で実装する。
    """

    def extract_top_patterns(
        self,
        df: pd.DataFrame,
        top_n: int = 20,
    ) -> pd.DataFrame:
        """言語別・クラスタ別のつまづきパターントップNを返す。"""
        raise NotImplementedError("Day 7 で実装")

    def label_clusters(self, df: pd.DataFrame) -> dict[int, str]:
        """各クラスタIDに対してTF-IDF上位語を使った説明ラベルを生成する。"""
        raise NotImplementedError("Day 7 で実装")
