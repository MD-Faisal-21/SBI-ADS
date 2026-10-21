from __future__ import annotations

from fastapi import APIRouter

from backend.shared import get_ml_context, require_ml_compatible
from ml.forecast_generator import generate_forecast

router = APIRouter(
    prefix="/forecast",
    tags=["Forecasting"],
)


@router.get("")


def get_forecast():
    dataset, _df, column_mapping = get_ml_context()

    require_ml_compatible(dataset["file_path"], column_mapping)

    forecast = generate_forecast(
        file_path=dataset["file_path"],
        column_mapping=column_mapping,
    ).copy()

    forecast["Last_Week"] = forecast["Last_Week"].astype(str)

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "forecast": forecast.to_dict(orient="records"),
    }
