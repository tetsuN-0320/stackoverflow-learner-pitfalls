"""Day 6: タグ共起ネットワーク分析を実行するスクリプト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from config.settings import ANALYSIS_DIR, PROCESSED_DIR, ROOT_DIR
from src.analysis.network import NetworkAnalyzer
from src.utils.logger import logger

LANGUAGES = ["python", "javascript", "java", "go"]


def main() -> None:
    questions_df = pd.read_parquet(PROCESSED_DIR / "questions.parquet")
    logger.info(f"質問数: {len(questions_df):,}")

    analyzer = NetworkAnalyzer()
    summary: list[dict] = []

    for lang in LANGUAGES:
        logger.info(f"\n=== {lang} ===")

        G = analyzer.build_cooccurrence_graph(questions_df, language=lang)
        partition = analyzer.detect_communities(G)
        centrality = analyzer.compute_centrality(G)

        # フロントエンド用 JSON を保存
        out_json = ROOT_DIR / "web" / "static" / "data" / "networks" / f"{lang}.json"
        analyzer.build_web_json(G, partition, centrality, out_json)

        # 媒介中心性トップ10を表示
        top = analyzer.top_nodes_by_centrality(centrality, top_n=10)
        print(f"\n[{lang}] 媒介中心性トップ10:")
        for tag, score in top:
            comm = partition.get(tag, -1)
            print(f"  {tag:<30} score={score:.4f}  community={comm}")

        summary.append(
            {
                "language": lang,
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "communities": len(set(partition.values())),
            }
        )

    print("\n=== ネットワーク概要 ===")
    for s in summary:
        print(
            f"  {s['language']:<12} "
            f"nodes={s['nodes']:>3}  edges={s['edges']:>4}  "
            f"communities={s['communities']}"
        )

    # ネットワーク指標を parquet で保存
    all_records = []
    for lang in LANGUAGES:
        G = analyzer.build_cooccurrence_graph(questions_df, language=lang)
        centrality = analyzer.compute_centrality(G)
        partition = analyzer.detect_communities(G)
        for node, cent in centrality.items():
            all_records.append(
                {
                    "language": lang,
                    "tag": node,
                    "frequency": G.nodes[node].get("frequency", 0),
                    "community": partition.get(node, 0),
                    **cent,
                }
            )

    net_df = pd.DataFrame(all_records)
    out_parquet = ANALYSIS_DIR / "network_centrality.parquet"
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    net_df.to_parquet(out_parquet, index=False)
    logger.info(f"network_centrality.parquet 保存: {out_parquet} ({len(net_df)} rows)")

    logger.info("Day 6 完了")


if __name__ == "__main__":
    main()
