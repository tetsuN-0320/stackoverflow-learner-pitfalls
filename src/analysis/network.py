from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd

from config.settings import NETWORK_TOP_N_NODES
from src.utils.logger import logger

try:
    import community as community_louvain  # python-louvain
    _HAS_LOUVAIN = True
except ImportError:
    _HAS_LOUVAIN = False
    logger.warning("python-louvain が未インストール。コミュニティ検出をスキップします。")


class NetworkAnalyzer:
    """メゾ層: タグ共起ネットワークの構築・分析を担うクラス。

    各質問が持つタグのペアを共起エッジとしてカウントし、
    networkx グラフを構築。Louvain 法でコミュニティを検出し、
    中心性指標（次数・媒介）でキーノードを特定する。
    """

    def build_cooccurrence_graph(
        self,
        df: pd.DataFrame,
        language: str,
        min_edge_weight: int = 3,
        top_n: int = NETWORK_TOP_N_NODES,
    ) -> nx.Graph:
        """質問サンプルからタグ共起グラフを構築する。

        min_edge_weight 未満の共起は除外してノイズを減らす。
        top_n は出現回数上位ノードに絞り込む閾値。
        """
        lang_df = df[df["language"] == language].copy()
        logger.info(f"[{language}] 質問数: {len(lang_df):,}")

        # ノード出現頻度でフィルタ（top_n に絞る）
        # tags 列は list / numpy.ndarray / str いずれも受け付ける
        def _to_list(tags) -> list[str]:
            if isinstance(tags, (list, tuple)):
                return list(tags)
            try:
                import numpy as np
                if isinstance(tags, np.ndarray):
                    return tags.tolist()
            except ImportError:
                pass
            if isinstance(tags, str):
                return tags.strip("[]").replace("'", "").split(", ")
            return []

        tag_counter: Counter = Counter()
        for tags in lang_df["tags"].dropna():
            tag_counter.update(_to_list(tags))

        top_tags = {tag for tag, _ in tag_counter.most_common(top_n)}

        # エッジ（共起ペア）をカウント
        edge_counter: Counter = Counter()
        for tags in lang_df["tags"].dropna():
            filtered = [t for t in _to_list(tags) if t in top_tags]
            for pair in combinations(sorted(filtered), 2):
                edge_counter[pair] += 1

        # グラフ構築
        G = nx.Graph()
        for tag, count in tag_counter.items():
            if tag in top_tags:
                G.add_node(tag, frequency=count)

        for (t1, t2), weight in edge_counter.items():
            if weight >= min_edge_weight:
                G.add_edge(t1, t2, weight=weight)

        # 孤立ノードは除去
        isolated = list(nx.isolates(G))
        G.remove_nodes_from(isolated)

        logger.info(
            f"[{language}] グラフ: {G.number_of_nodes()} ノード, "
            f"{G.number_of_edges()} エッジ (孤立{len(isolated)}個除去)"
        )
        return G

    def detect_communities(self, G: nx.Graph) -> dict[str, int]:
        """Louvain 法でコミュニティを検出し、ノード → コミュニティIDの辞書を返す。

        python-louvain が使えない場合はすべて community=0 にフォールバック。
        """
        if not _HAS_LOUVAIN or G.number_of_nodes() == 0:
            return {node: 0 for node in G.nodes()}

        partition: dict[str, int] = community_louvain.best_partition(G, weight="weight")
        n_communities = len(set(partition.values()))
        logger.info(f"コミュニティ数: {n_communities}")
        return partition

    def compute_centrality(self, G: nx.Graph) -> dict[str, dict[str, float]]:
        """次数中心性・媒介中心性を計算する。

        Returns:
            {node: {"degree_centrality": float, "betweenness_centrality": float}}
        """
        if G.number_of_nodes() == 0:
            return {}

        degree_cent = nx.degree_centrality(G)
        # 大きなグラフでは近似計算（k=min(100, n)）で高速化
        k = min(100, G.number_of_nodes())
        betweenness_cent = nx.betweenness_centrality(G, weight="weight", k=k, normalized=True)

        return {
            node: {
                "degree_centrality": round(degree_cent[node], 4),
                "betweenness_centrality": round(betweenness_cent[node], 4),
            }
            for node in G.nodes()
        }

    def build_web_json(
        self,
        G: nx.Graph,
        partition: dict[str, int],
        centrality: dict[str, dict[str, float]],
        output_path: Path,
    ) -> None:
        """D3.js force-directed graph 用の JSON を生成する。

        形式:
          {
            "nodes": [{"id": tag, "frequency": N, "community": C,
                       "degree_centrality": x, "betweenness_centrality": x}],
            "links": [{"source": t1, "target": t2, "weight": N}]
          }
        """
        nodes: list[dict[str, Any]] = []
        for node in G.nodes():
            freq = G.nodes[node].get("frequency", 0)
            cent = centrality.get(node, {})
            nodes.append(
                {
                    "id": node,
                    "frequency": freq,
                    "community": partition.get(node, 0),
                    "degree_centrality": cent.get("degree_centrality", 0.0),
                    "betweenness_centrality": cent.get("betweenness_centrality", 0.0),
                }
            )

        links: list[dict[str, Any]] = [
            {"source": u, "target": v, "weight": data["weight"]}
            for u, v, data in G.edges(data=True)
        ]

        payload = {"nodes": nodes, "links": links}
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        logger.info(
            f"network.json 出力: {output_path} "
            f"({len(nodes)} nodes, {len(links)} links)"
        )

    def top_nodes_by_centrality(
        self,
        centrality: dict[str, dict[str, float]],
        metric: str = "betweenness_centrality",
        top_n: int = 20,
    ) -> list[tuple[str, float]]:
        """中心性指標で上位ノードを返す。"""
        ranked = sorted(
            ((node, vals[metric]) for node, vals in centrality.items()),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_n]
