from __future__ import annotations

from fastapi import APIRouter

from analytics.inventory_intelligence import generate_inventory_recommendations
from backend.shared import get_ml_context, require_ml_compatible
from core import config

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory Intelligence"],
)


@router.get("")


def get_inventory_intelligence():
    dataset, _df, column_mapping = get_ml_context()

    require_ml_compatible(dataset["file_path"], column_mapping)

    recommendations = generate_inventory_recommendations(
        file_path=dataset["file_path"],
        column_mapping=column_mapping,
    )

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "safety_buffer": f"{config.SAFETY_BUFFER * 100:.0f}%",
        "recommendations": recommendations,
    }
