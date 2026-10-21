from __future__ import annotations

from database.connection import execute, query_all, query_one

_LIST_COLUMNS = """
    dataset_id, file_name, file_type, upload_date,
    row_count, column_count, processing_status
"""

_DETAIL_COLUMNS = """
    dataset_id, file_name, file_path, file_type, upload_date,
    row_count, column_count, processing_status
"""


def _serialise(row: dict | None) -> dict | None:
    if row and "upload_date" in row and row["upload_date"] is not None:
        row["upload_date"] = str(row["upload_date"])
    return row


def save_dataset(
    file_name: str,
    file_path: str,
    file_type: str,
    row_count: int,
    column_count: int,
    processing_status: str = "Uploaded",
) -> int:
    return execute(
        """
        INSERT INTO datasets
            (file_name, file_path, file_type, row_count, column_count, processing_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (file_name, file_path, file_type, row_count, column_count, processing_status),
    )


def get_all_datasets() -> list[dict]:
    rows = query_all(
        f"""
        SELECT {_LIST_COLUMNS}
        FROM datasets
        ORDER BY upload_date DESC, dataset_id DESC
        """
    )
    return [_serialise(row) for row in rows]


def get_latest_dataset() -> dict | None:
    row = query_one(
        f"""
        SELECT {_DETAIL_COLUMNS}
        FROM datasets
        WHERE processing_status = 'Completed'
        ORDER BY dataset_id DESC
        LIMIT 1
        """
    )
    return _serialise(row)
