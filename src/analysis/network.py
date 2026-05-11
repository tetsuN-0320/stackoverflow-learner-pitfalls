from __future__ import annotations

import networkx as nx
import pandas as pd


class TagNetworkBuilder:
    """メゾ層: タグ共起ネットワークの構築とコミュニティ検出を担うクラス。

    networkx でグラフを構築し、Louvain法でコミュニティを検出する。
    Day 6 で実装する。
    """

    def build_cooccurrence_graph(self, df: pd.DataFrame, top_n: int = 75) -> nx.Graph:
        """質問タグの共起グラフを構築する。ノードは上位N個に絞る。"""
        raise NotImplementedError("Day 6 で実装")

    def detect_communities(self, graph: nx.Graph) -> dict[str, int]:
        """Louvain法でコミュニティIDを割り当てる。ノード名→コミュニティIDの辞書を返す。"""
        raise NotImplementedError("Day 6 で実装")

    def compute_centrality(self, graph: nx.Graph) -> dict[str, float]:
        """各ノードの媒介中心性を計算する。学習領域の中核タグ特定に使う。"""
        raise NotImplementedError("Day 6 で実装")
