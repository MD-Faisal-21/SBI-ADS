from __future__ import annotations

from fastapi import APIRouter

from analytics.ml_decision_engine import generate_ml_recommendations
from backend.shared import get_ml_context, require_ml_compatible

router = APIRouter(
    prefix="/decision",
    tags=["Decision Support"],
)


@router.get("")


def get_decision_support():
    dataset, _df, column_mapping = get_ml_context()

    require_ml_compatible(dataset["file_path"], column_mapping)

    recommendations = generate_ml_recommendations(
        file_path=dataset["file_path"],
        column_mapping=column_mapping,
    )

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "recommendations": recommendations,
    }
