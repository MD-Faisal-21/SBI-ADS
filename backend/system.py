from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.dashboard import get_latest_analysis
from core import config
from database.connection import database_status

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

START_TIME = time.time()


@router.get("/health")


def get_health():
    dataset = None

    try:
        dataset, _analysis = get_latest_analysis()
        dataset_name = dataset["file_name"]
        dataset_id = dataset["dataset_id"]
    except HTTPException:
        dataset_name = None
        dataset_id = None

    charts_available = 0
    if config.CHART_DIR.exists():
        charts_available = len(list(config.CHART_DIR.glob("*.png")))

    return {
        "status": "ok",
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "database": database_status(),
        "charts_available": charts_available,
        "currency": config.CURRENCY_SYMBOL,
        "locale": config.NUMBER_LOCALE,
        "latest_dataset": {
            "dataset_id": dataset_id,
            "file_name": dataset_name,
        },
    }


@router.get("/report")


def export_report():
    dataset, analysis = get_latest_analysis()

    payload = {
        "report_metadata": {
            "app": config.APP_NAME,
            "version": config.APP_VERSION,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "dataset_id": dataset["dataset_id"],
            "file_name": dataset["file_name"],
        },
        "analysis": analysis,
    }

    content = json.dumps(payload, default=str, indent=2)

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition": (
                f'attachment; filename="sbi-ads-report-{dataset["dataset_id"]}.json"'
            )
        },
    )
