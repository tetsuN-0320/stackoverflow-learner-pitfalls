"""Day 8: フロントエンド用 JSON を生成して web/static/data/ に書き出す CLI スクリプト。

生成するファイル:
  - web/static/data/trends.json    : マクロ分析（年別指標 + Developer Survey）
  - web/static/data/networks/*.json: メゾ分析ネットワーク（上位50ノードに絞り込み済み）
  - web/static/data/pitfalls.json  : ミクロ分析（run_micro_analysis.py で生成済み、存在確認のみ）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import yaml

from config.settings import ANALYSIS_DIR, PROCESSED_DIR, ROOT_DIR
from src.utils.logger import logger

WEB_DATA_DIR = ROOT_DIR / "web" / "static" / "data"
NETWORK_SRC_DIR = WEB_DATA_DIR / "networks"
LANG_CONFIG_PATH = ROOT_DIR / "config" / "target_languages.yml"
LANGUAGES = ["python", "javascript", "java", "go"]
TOP_NODES = 50  # ネットワーク図に表示するノード数の上限


# ─────────────────────────────────────────────
# 1. trends.json
# ─────────────────────────────────────────────

def build_trends_json(output_path: Path) -> None:
    """trends.parquet から年別指標 + Developer Survey を整形して trends.json を生成する。

    フロントエンドで使う 2 系列:
      - yearly: 2015〜2024 の年別指標（中央スコア・閲覧数・回答率）→折れ線グラフ
      - survey: 2022〜2024 の Developer Survey 使用率・希望率 → 棒グラフ
    """
    trends_df = pd.read_parquet(ANALYSIS_DIR / "trends.parquet")
    tags_df = pd.read_parquet(PROCESSED_DIR / "tags.parquet")

    with open(LANG_CONFIG_PATH, encoding="utf-8") as f:
        lang_cfg = yaml.safe_load(f)["languages"]

    all_years = sorted(trends_df["year"].unique().tolist())
    survey_years = sorted(
        trends_df.dropna(subset=["usage_pct"])["year"].unique().tolist()
    )

    languages: dict[str, dict] = {}
    for lang in LANGUAGES:
        sub = trends_df[trends_df["language"] == lang].sort_values("year")
        cfg = lang_cfg.get(lang, {})

        # タグ統計から総質問数を取得
        tag_row = tags_df[tags_df["name"] == lang]
        total_q = int(tag_row["count"].iloc[0]) if not tag_row.empty else 0

        # 年別指標（全年）
        yearly: dict[str, list] = {
            "median_score": [],
            "median_views": [],
            "answer_rate": [],
        }
        for year in all_years:
            row = sub[sub["year"] == year]
            if row.empty:
                yearly["median_score"].append(None)
                yearly["median_views"].append(None)
                yearly["answer_rate"].append(None)
            else:
                yearly["median_score"].append(
                    round(float(row["median_score"].iloc[0]), 2)
                )
                yearly["median_views"].append(
                    round(float(row["median_views"].iloc[0]), 0)
                )
                yearly["answer_rate"].append(
                    round(float(row["answer_rate"].iloc[0]), 3)
                )

        # Developer Survey 指標（survey_years のみ）
        survey_sub = sub.dropna(subset=["usage_pct"]).sort_values("year")
        survey: dict[str, list] = {
            "usage_pct": survey_sub["usage_pct"].tolist(),
            "want_pct": survey_sub["want_pct"].tolist(),
        }

        languages[lang] = {
            "display_name": cfg.get("display_name", lang),
            "color": cfg.get("color", "#888888"),
            "total_questions": total_q,
            "yearly": yearly,
            "survey": survey,
        }
        logger.info(
            f"[trends] {lang}: {len(all_years)}年分 / survey={survey_sub['usage_pct'].tolist()}"
        )

    payload = {
        "years": all_years,
        "survey_years": survey_years,
        "languages": languages,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info(f"trends.json 出力: {output_path}")


# ─────────────────────────────────────────────
# 2. networks/*.json
# ─────────────────────────────────────────────

def trim_network_json(src_path: Path, dst_path: Path, top_n: int = TOP_NODES) -> None:
    """ネットワーク JSON を読み込み、上位 top_n ノードに絞り込んで書き出す。

    ノードの選択基準: betweenness_centrality 降順（上位 top_n 個）。
    ハブノード（言語名タグ）は必ず含める。
    選択ノード間のリンクのみ残す。
    """
    with open(src_path, encoding="utf-8") as f:
        data = json.load(f)

    nodes: list[dict] = data["nodes"]
    links: list[dict] = data["links"]

    # betweenness_centrality 降順でノードをソート
    nodes_sorted = sorted(
        nodes, key=lambda n: n.get("betweenness_centrality", 0), reverse=True
    )
    selected = nodes_sorted[:top_n]
    selected_ids = {n["id"] for n in selected}

    # 両端が selected_ids に含まれるリンクのみ残す
    trimmed_links = [
        lk for lk in links
        if lk["source"] in selected_ids and lk["target"] in selected_ids
    ]

    result = {"nodes": selected, "links": trimmed_links}
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(
        f"[network] {src_path.stem}: {len(nodes)}ノード→{len(selected)}ノード / "
        f"リンク {len(links)}→{len(trimmed_links)}"
    )


def build_network_jsons(src_dir: Path, dst_dir: Path) -> None:
    for lang in LANGUAGES:
        src = src_dir / f"{lang}.json"
        dst = dst_dir / f"{lang}.json"
        if not src.exists():
            logger.warning(f"ネットワーク JSON が見つかりません: {src}")
            continue
        trim_network_json(src, dst)


# ─────────────────────────────────────────────
# 3. pitfalls.json 存在確認
# ─────────────────────────────────────────────

def verify_pitfalls_json(path: Path) -> None:
    if not path.exists():
        logger.error(
            f"pitfalls.json が見つかりません: {path}\n"
            "  → scripts/run_micro_analysis.py を先に実行してください。"
        )
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for lang in LANGUAGES:
        n = len(data.get(lang, []))
        logger.info(f"[pitfalls] {lang}: {n}クラスタ")


# ─────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────

def main() -> None:
    logger.info("=== build_site.py: フロントエンド用JSON生成 ===")

    logger.info("\n--- 1. trends.json ---")
    build_trends_json(WEB_DATA_DIR / "trends.json")

    logger.info("\n--- 2. networks/*.json (上位50ノードに絞り込み) ---")
    build_network_jsons(NETWORK_SRC_DIR, NETWORK_SRC_DIR)

    logger.info("\n--- 3. pitfalls.json 確認 ---")
    verify_pitfalls_json(WEB_DATA_DIR / "pitfalls.json")

    logger.info("\n=== 完了 ===")
    logger.info(f"  出力先: {WEB_DATA_DIR}")


if __name__ == "__main__":
    main()
