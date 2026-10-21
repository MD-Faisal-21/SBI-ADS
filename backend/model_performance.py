from __future__ import annotations

import numpy as np
from fastapi import APIRouter

from backend.shared import get_ml_context, require_ml_compatible
from ml.forecast_validation import validate_model

router = APIRouter(
    prefix="/model-performance",
    tags=["ML Model Performance"],
)


@router.get("")


def get_model_performance():
    dataset, _df, column_mapping = get_ml_context()

    require_ml_compatible(dataset["file_path"], column_mapping)

    (
        model,
        comparison,
        mae,
        rmse,
        r2,
        training_weeks,
        testing_weeks,
    ) = validate_model(
        file_path=dataset["file_path"],
        column_mapping=column_mapping,
    )

    model_name = type(model.named_steps["model"]).__name__

    actual = comparison["Weekly_Quantity"].to_numpy(dtype=float)
    predicted = comparison["Predicted_Quantity"].to_numpy(dtype=float)
    non_zero = actual[actual != 0]

    mape = (
        float(np.mean(np.abs((non_zero - predicted[actual != 0]) / non_zero)) * 100)
        if non_zero.size
        else None
    )

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "model": model_name,
        "training_weeks": training_weeks,
        "testing_weeks": testing_weeks,
        "metrics": {
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "r2": round(float(r2), 2),
            "mape": round(mape, 2) if mape is not None else None,
        },
        "validation_results": comparison.to_dict(orient="records"),
    }
