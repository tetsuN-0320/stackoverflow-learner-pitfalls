from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


class PitfallBarChart:
    """つまづきトップNの横棒グラフを生成するクラス。Day 7・8 で実装。"""

    def build(self, df: pd.DataFrame, language: str, top_n: int = 20) -> go.Figure:
        """言語別つまづきパターンをスコア順に並べた横棒グラフを生成する。"""
        raise NotImplementedError("Day 7 で実装")
