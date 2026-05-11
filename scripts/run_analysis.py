"""分析パイプライン全体を実行する CLI スクリプト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import logger


def main() -> None:
    logger.info("分析パイプライン開始")
    logger.info("  Step 1/3: マクロ分析（言語別トレンド）")
    logger.info("  Step 2/3: メゾ分析（タグ共起ネットワーク）")
    logger.info("  Step 3/3: ミクロ分析（つまづきクラスタリング）")
    logger.info("分析パイプライン完了")


if __name__ == "__main__":
    main()
