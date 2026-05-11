from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


class NetworkExporter:
    """D3.js force-directed graph 用 JSON を生成するクラス。

    {"nodes": [...], "links": [...]} 形式で言語別ファイルに書き出す。
    Day 6・8 で実装する。
    """

    def to_d3_json(self, graph: nx.Graph, communities: dict[str, int]) -> dict:
        """networkx グラフを D3.js 用の nodes/links 辞書に変換する。"""
        raise NotImplementedError("Day 8 で実装")

    def export(self, graph: nx.Graph, communities: dict[str, int], output_path: Path) -> None:
        """D3.js 用 JSON をファイルに書き出す。"""
        data = self.to_d3_json(graph, communities)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
