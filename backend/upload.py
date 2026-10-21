from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from analytics.pipeline import run_pipeline
from core import config
from database.dataset_repository import get_all_datasets, save_dataset

router = APIRouter()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    original_name = file.filename or "dataset"

    if not original_name.lower().endswith(config.ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel (.xlsx) files are supported.",
        )

    config.ensure_directories()

    max_bytes = config.MAX_UPLOAD_MB * 1024 * 1024
    contents = await file.read(max_bytes + 1)

    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds the {config.MAX_UPLOAD_MB} MB upload limit. "
                "Export a sample or aggregate the data before uploading."
            ),
        )

    if not contents:
        raise HTTPException(status_code=422, detail="The uploaded file is empty.")

    safe_suffix = Path(original_name).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{safe_suffix}"
    file_path = os.path.join(str(config.UPLOAD_DIR), unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    try:
        analysis_result = run_pipeline(file_path)
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed while processing the dataset: {error}",
        ) from error

    analysis_file = file_path + ".analysis.json"
    temp_file = analysis_file + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as handle:
        json.dump(analysis_result, handle, default=str, indent=2)

    os.replace(temp_file, analysis_file)

    file_type = safe_suffix.lstrip(".")

    dataset_id = save_dataset(
        file_name=original_name,
        file_path=file_path,
        file_type=file_type,
        row_count=analysis_result["profile"]["rows"],
        column_count=analysis_result["profile"]["columns"],
        processing_status="Completed",
    )

    return {
        "message": "Dataset analyzed successfully!",
        "dataset_id": dataset_id,
        "file_name": original_name,
        "analysis": analysis_result,
    }


@router.get("/datasets")
async def get_datasets():
    return {"datasets": get_all_datasets()}
