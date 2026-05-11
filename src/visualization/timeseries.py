from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


class TimeseriesChart:
    """言語別質問数トレンドの折れ線グラフを生成するクラス。Day 5 で実装。"""

    def build(self, df: pd.DataFrame) -> go.Figure:
        """言語×年の質問数データからPlotly折れ線グラフを生成する。"""
        raise NotImplementedError("Day 5 で実装")
