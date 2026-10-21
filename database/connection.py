from __future__ import annotations

import sqlite3
from typing import Any, Iterable, Optional

from core import config


class DatabaseUnavailableError(RuntimeError):
    pass


def _sqlite_connect() -> sqlite3.Connection:
    connection = sqlite3.connect(str(config.DB_SQLITE_PATH))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL;")
    return connection


def _mysql_connect():
    try:
        import mysql.connector
    except ImportError as error:
        raise DatabaseUnavailableError(
            "mysql-connector-python is not installed. "
            "Install it or set SBI_DB_DRIVER=sqlite."
        ) from error

    return mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )


def get_connection():
    if config.DB_DRIVER == "mysql":
        return _mysql_connect()
    return _sqlite_connect()

SCHEMA_STATEMENTS = {
    "sqlite": """
        CREATE TABLE IF NOT EXISTS datasets (
            dataset_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name         TEXT NOT NULL,
            file_path         TEXT NOT NULL,
            file_type         TEXT NOT NULL,
            upload_date       DATETIME DEFAULT CURRENT_TIMESTAMP,
            row_count         INTEGER DEFAULT 0,
            column_count      INTEGER DEFAULT 0,
            processing_status TEXT DEFAULT 'Uploaded'
        );
    """,
    "mysql": """
        CREATE TABLE IF NOT EXISTS datasets (
            dataset_id        INT AUTO_INCREMENT PRIMARY KEY,
            file_name         VARCHAR(255) NOT NULL,
            file_path         VARCHAR(512) NOT NULL,
            file_type         VARCHAR(16) NOT NULL,
            upload_date       DATETIME DEFAULT CURRENT_TIMESTAMP,
            row_count         INT DEFAULT 0,
            column_count      INT DEFAULT 0,
            processing_status VARCHAR(32) DEFAULT 'Uploaded'
        );
    """,
}


def initialise_schema() -> None:
    driver = config.DB_DRIVER
    statement = SCHEMA_STATEMENTS.get(driver, SCHEMA_STATEMENTS["sqlite"])

    connection = get_connection()
    try:
        if driver == "mysql":
            cursor = connection.cursor()
            cursor.execute(statement)
            cursor.close()
        else:
            connection.executescript(statement)
        connection.commit()
    finally:
        connection.close()


def database_status() -> dict:
    try:
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchall()
            cursor.close()
        finally:
            connection.close()
        return {"driver": config.DB_DRIVER, "connected": True}
    except Exception as error:
        return {"driver": config.DB_DRIVER, "connected": False, "error": str(error)}


def _prepare(sql: str) -> str:
    if config.DB_DRIVER == "mysql":
        return sql.replace("?", "%s")
    return sql


def _fetch_rows(cursor) -> list[dict]:
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def query_all(sql: str, params: Optional[Iterable[Any]] = None) -> list[dict]:
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True) if config.DB_DRIVER == "mysql" else connection.cursor()
        cursor.execute(_prepare(sql), tuple(params or ()))
        rows = _fetch_rows(cursor)
        cursor.close()
        return rows
    finally:
        connection.close()


def query_one(sql: str, params: Optional[Iterable[Any]] = None) -> Optional[dict]:
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: Optional[Iterable[Any]] = None) -> int:
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True) if config.DB_DRIVER == "mysql" else connection.cursor()
        cursor.execute(_prepare(sql), tuple(params or ()))
        connection.commit()
        lastrowid = cursor.lastrowid
        cursor.close()
        return int(lastrowid) if lastrowid is not None else 0
    finally:
        connection.close()
