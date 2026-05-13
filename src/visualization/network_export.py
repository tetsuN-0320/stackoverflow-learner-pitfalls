from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


class NetworkExporter:
    """D3.js force-directed graph 用 JSON を生成するクラス。

    {"nodes": [...], "links": [...]} 形式で言語別ファイルに書き出す。
    """

    def to_d3_json(
        self,
        graph: nx.Graph,
        communities: dict[str, int],
        top_n: int = 50,
    ) -> dict:
        """networkx グラフを D3.js 用の nodes/links 辞書に変換する。

        betweenness_centrality 上位 top_n ノードに絞り込み、
        選択ノード間のリンクのみ残す。
        """
        betweenness = nx.betweenness_centrality(graph)
        degree = nx.degree_centrality(graph)

        # 上位 top_n ノードを選択
        top_nodes = sorted(betweenness, key=betweenness.get, reverse=True)[:top_n]
        top_set = set(top_nodes)

        nodes = [
            {
                "id": node,
                "frequency": graph.nodes[node].get("frequency", 0),
                "community": communities.get(node, 0),
                "degree_centrality": round(degree[node], 4),
                "betweenness_centrality": round(betweenness[node], 4),
            }
            for node in top_nodes
        ]

        links = [
            {
                "source": u,
                "target": v,
                "weight": data.get("weight", 1),
            }
            for u, v, data in graph.edges(data=True)
            if u in top_set and v in top_set
        ]

        return {"nodes": nodes, "links": links}

    def export(
        self,
        graph: nx.Graph,
        communities: dict[str, int],
        output_path: Path,
        top_n: int = 50,
    ) -> None:
        """D3.js 用 JSON をファイルに書き出す。"""
        data = self.to_d3_json(graph, communities, top_n=top_n)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
