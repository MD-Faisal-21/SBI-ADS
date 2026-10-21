from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

APP_NAME = "SBI-ADS"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = (
    "Smart Business Intelligence & AI Decision Support System — "
    "upload business data and receive KPIs, interactive analytics, "
    "ML demand forecasts, anomaly alerts and actionable recommendations."
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("SBI_DATA_DIR", str(BASE_DIR / "data")))
UPLOAD_DIR = DATA_DIR / "uploads"
CHART_DIR = DATA_DIR / "charts"
FRONTEND_DIR = BASE_DIR / "frontend"

MAX_UPLOAD_MB = int(os.getenv("SBI_MAX_UPLOAD_MB", "25"))
ALLOWED_EXTENSIONS = (".csv", ".xlsx")

CURRENCY_SYMBOL = os.getenv("SBI_CURRENCY_SYMBOL", "₹")
NUMBER_LOCALE = os.getenv("SBI_NUMBER_LOCALE", "en-IN")

_host = os.getenv("SBI_DB_HOST", "")
_driver = os.getenv("SBI_DB_DRIVER", "").lower()

DB_DRIVER = _driver if _driver in ("sqlite", "mysql") else ("mysql" if _host else "sqlite")

DB_SQLITE_PATH = Path(os.getenv("SBI_SQLITE_PATH", str(DATA_DIR / "sbi_ads.db")))
DB_HOST = _host or "localhost"
DB_PORT = int(os.getenv("SBI_DB_PORT", "3306"))
DB_USER = os.getenv("SBI_DB_USER", "root")
DB_PASSWORD = os.getenv("SBI_DB_PASSWORD", "admin")
DB_NAME = os.getenv("SBI_DB_NAME", "sbi_ads")

SAFETY_BUFFER = float(os.getenv("SBI_SAFETY_BUFFER", "0.10"))
ANOMALY_Z_THRESHOLD = float(os.getenv("SBI_ANOMALY_Z_THRESHOLD", "3.0"))


def ensure_directories() -> None:
    for directory in (DATA_DIR, UPLOAD_DIR, CHART_DIR, DB_SQLITE_PATH.parent):
        directory.mkdir(parents=True, exist_ok=True)
