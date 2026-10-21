from __future__ import annotations

import json
import math
import os

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.shared import get_ml_context
from database.dataset_repository import get_latest_dataset

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def get_latest_analysis() -> tuple[dict, dict]:
    dataset = get_latest_dataset()

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="No dataset has been uploaded yet. Upload a file to begin.",
        )

    analysis_file = dataset["file_path"] + ".analysis.json"

    if not os.path.exists(analysis_file):
        raise HTTPException(
            status_code=404,
            detail="Analysis result not found. Please re-upload the dataset.",
        )

    try:
        with open(analysis_file, "r", encoding="utf-8") as handle:
            analysis = json.load(handle)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load analysis: {error}",
        ) from error

    return dataset, analysis


def _clean_float(value):
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


@router.get("")


def get_dashboard():
    dataset, analysis = get_latest_analysis()

    kpis = analysis.get("kpis", {})
    profile = analysis.get("profile", {})

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "row_count": profile.get("rows", 0),
        "column_count": profile.get("columns", 0),
        "total_revenue": kpis.get("total_revenue", 0),
        "total_quantity": kpis.get("total_quantity", 0),
        "total_products": kpis.get("total_products", 0),
        "total_customers": kpis.get("total_customers", 0),
        "total_locations": kpis.get("total_locations", 0),
        "top_product": kpis.get("top_product", "—"),
        "top_location": kpis.get("top_location", "—"),
        "average_price": kpis.get("average_price", 0),
        "average_order_value": kpis.get("average_order_value", 0),
    }


@router.get("/insights")


def get_dashboard_insights():
    dataset, analysis = get_latest_analysis()

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "insights": analysis.get("insights", []),
    }


@router.get("/recommendations")


def get_dashboard_recommendations():
    dataset, analysis = get_latest_analysis()

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "recommendations": analysis.get("recommendations", []),
    }


@router.get("/anomalies")


def get_dashboard_anomalies():
    dataset, analysis = get_latest_analysis()

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "anomalies": analysis.get("anomalies", []),
    }


@router.get("/analytics")


def get_dashboard_analytics():
    dataset, df, mapping = get_ml_context()

    column_by_type = {}
    for column, semantic_type in mapping.items():
        column_by_type.setdefault(semantic_type, column)

    date_column = column_by_type.get("date")
    product_column = column_by_type.get("product")
    quantity_column = column_by_type.get("quantity")
    price_column = column_by_type.get("unit_price")
    location_column = column_by_type.get("location")
    category_column = column_by_type.get("category")

    working = df.copy()

    if quantity_column and price_column:
        working["_revenue"] = (
            pd.to_numeric(working[quantity_column], errors="coerce")
            * pd.to_numeric(working[price_column], errors="coerce")
        )
    elif price_column:
        working["_revenue"] = pd.to_numeric(working[price_column], errors="coerce")
    elif quantity_column:
        working["_revenue"] = pd.to_numeric(working[quantity_column], errors="coerce")
    else:
        working["_revenue"] = 0

    working["_revenue"] = working["_revenue"].fillna(0)

    revenue_trend = []

    if date_column:
        working[date_column] = pd.to_datetime(
            working[date_column], errors="coerce"
        )
        trend_df = working.dropna(subset=[date_column])

        if not trend_df.empty:
            grouped = trend_df.groupby(
                trend_df[date_column].dt.date
            ).agg(
                revenue=("_revenue", "sum"),
                **(
                    {"quantity": (quantity_column, "sum")}
                    if quantity_column
                    else {}
                ),
            )
            grouped = grouped.sort_index().tail(120)

            for trend_date, row in grouped.iterrows():
                point = {
                    "date": str(trend_date),
                    "revenue": _clean_float(row["revenue"]),
                }
                if quantity_column:
                    point["quantity"] = _clean_float(row.get("quantity"))
                revenue_trend.append(point)

    product_performance = []

    if product_column:
        product_data = (
            working.groupby(product_column)["_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        product_performance = [
            {"label": str(label), "value": _clean_float(value)}
            for label, value in product_data.items()
        ]

    regional_performance = []

    if location_column:
        location_data = (
            working.groupby(location_column)["_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        regional_performance = [
            {"label": str(label), "value": _clean_float(value)}
            for label, value in location_data.items()
        ]

    category_mix = []

    if category_column:
        category_data = (
            working.groupby(category_column)["_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(8)
        )
        category_mix = [
            {"label": str(label), "value": _clean_float(value)}
            for label, value in category_data.items()
        ]

    price_distribution = []

    if price_column:
        prices = pd.to_numeric(working[price_column], errors="coerce").dropna()

        if not prices.empty and prices.nunique() > 1:
            counts, bin_edges = np.histogram(prices, bins=13)
            price_distribution = [
                {
                    "label": f"{bin_edges[index]:,.0f}",
                    "value": int(count),
                }
                for index, count in enumerate(counts)
            ]
        elif not prices.empty:
            price_distribution = [
                {"label": f"{prices.iloc[0]:,.0f}", "value": int(len(prices))}
            ]

    numeric_df = working.select_dtypes(include="number").dropna(axis=1, how="all")

    correlation_labels = []
    correlation_values = []

    if numeric_df.shape[1] > 1:
        correlation = numeric_df.corr().round(2)
        correlation_labels = list(correlation.columns)
        correlation_values = [
            [_clean_float(cell) for cell in row]
            for row in correlation.values.tolist()
        ]

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "revenue_trend": revenue_trend,
        "product_performance": product_performance,
        "regional_performance": regional_performance,
        "category_mix": category_mix,
        "price_distribution": price_distribution,
        "correlation": {
            "labels": correlation_labels,
            "values": correlation_values,
        },
    }


@router.get("/quality")


def get_data_quality():
    dataset, analysis = get_latest_analysis()

    profile = analysis.get("profile", {})
    cleaning = analysis.get("cleaning", {})

    rows = int(profile.get("rows", 0))
    column_details = profile.get("column_details", [])

    missing_cells = sum(int(col.get("missing_values", 0)) for col in column_details)
    total_cells = rows * len(column_details) if column_details else 0
    completeness = (
        round(100 * (1 - missing_cells / total_cells), 1)
        if total_cells
        else 100.0
    )

    duplicates_removed = int(cleaning.get("duplicates_removed", 0) or 0)
    original_rows = int(cleaning.get("original_rows", rows) or rows)
    duplicate_free = (
        round(100 * (1 - duplicates_removed / original_rows), 1)
        if original_rows
        else 100.0
    )

    quality_score = round(0.7 * completeness + 0.3 * duplicate_free, 1)

    columns = [
        {
            "name": col.get("name"),
            "data_type": col.get("data_type"),
            "missing_values": int(col.get("missing_values", 0)),
            "unique_values": col.get("unique_values"),
        }
        for col in column_details
    ]

    return {
        "dataset_id": dataset["dataset_id"],
        "file_name": dataset["file_name"],
        "rows_before": original_rows,
        "rows_after": int(cleaning.get("final_rows", rows) or rows),
        "duplicates_removed": duplicates_removed,
        "missing_cells": missing_cells,
        "completeness_percent": completeness,
        "duplicate_free_percent": duplicate_free,
        "quality_score": quality_score,
        "columns": columns,
    }
