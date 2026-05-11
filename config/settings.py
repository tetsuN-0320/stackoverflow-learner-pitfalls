from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent.parent

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ANALYSIS_DIR = DATA_DIR / "analysis"

STACKEX_API_KEY: str = os.getenv("STACKEX_API_KEY", "")
STACKEX_APP_NAME: str = os.getenv("STACKEX_APP_NAME", "stackoverflow-learner-pitfalls")
STACKEX_BASE_URL: str = "https://api.stackexchange.com/2.3"
STACKEX_MAX_REQUESTS_PER_DAY: int = 10_000
STACKEX_PAGE_SIZE: int = 100

ANALYSIS_START_YEAR: int = 2015
ANALYSIS_END_YEAR: int = 2024
NETWORK_TOP_N_NODES: int = 75
PITFALL_TOP_N: int = 20
