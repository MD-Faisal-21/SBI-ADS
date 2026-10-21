from __future__ import annotations

import pandas as pd
from fastapi import HTTPException

from analytics.column_detector import detect_columns
from database.dataset_repository import get_latest_dataset
from ml.dataset_adapter import check_ml_compatibility


def load_latest_dataframe() -> tuple[dict, pd.DataFrame]:
    dataset = get_latest_dataset()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=(
                "No dataset has been uploaded yet. "
                "Upload a CSV or Excel file from the dashboard to begin."
            ),
        )

    file_path = dataset.get("file_path")

    if not file_path:
        raise HTTPException(
            status_code=400,
            detail="Stored file path is missing for the latest dataset.",
        )

    try:
        if dataset["file_type"] == "xlsx":
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=410,
            detail=(
                "The stored dataset file no longer exists on the server. "
                "Please upload the dataset again."
            ),
        ) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read the stored dataset: {error}",
        ) from error

    if df.empty:
        raise HTTPException(
            status_code=422,
            detail="The stored dataset is empty.",
        )

    return dataset, df


def get_ml_context() -> tuple[dict, pd.DataFrame, dict]:
    dataset, df = load_latest_dataframe()
    column_mapping = detect_columns(df)
    return dataset, df, column_mapping


def require_ml_compatible(file_path: str, column_mapping: dict) -> dict:
    compatibility = check_ml_compatibility(file_path, column_mapping)

    if not compatibility.get("compatible"):
        raise HTTPException(
            status_code=422,
            detail=compatibility.get(
                "reason",
                "Dataset is not compatible with demand forecasting.",
            ),
        )

    return compatibility
