from __future__ import annotations

import pandas as pd

from analytics.chart_engine import generate_charts
from analytics.anomaly_detector import detect_anomalies
from analytics.column_detector import detect_columns
from analytics.data_cleaner import clean_dataset
from analytics.data_profiler import profile_dataset
from analytics.decision_engine import generate_recommendations
from analytics.eda_engine import perform_eda
from analytics.insight_engine import generate_insights
from analytics.kpi_engine import calculate_kpis


def run_pipeline(file_path: str) -> dict:
    profile = profile_dataset(file_path)

    cleaning_result = clean_dataset(file_path)
    cleaned_df = cleaning_result["cleaned_data"]

    detected_columns = detect_columns(cleaned_df)

    kpis = calculate_kpis(cleaned_df, detected_columns)

    eda_results = perform_eda(cleaned_df, detected_columns)

    charts = generate_charts(cleaned_df, detected_columns)

    insights = generate_insights(cleaned_df, kpis, eda_results, detected_columns)

    recommendations = generate_recommendations(
        cleaned_df, kpis, eda_results, detected_columns
    )

    try:
        if str(file_path).lower().endswith((".xlsx", ".xls")):
            raw_df = pd.read_excel(file_path)
        else:
            raw_df = pd.read_csv(file_path)

        anomalies = detect_anomalies(
            file_path=file_path,
            column_mapping=detect_columns(raw_df),
        )
    except Exception:
        anomalies = []

    return {
        "profile": {
            "rows": profile["rows"],
            "columns": profile["columns"],
            "duplicate_rows": profile.get("duplicate_rows", 0),
            "column_details": profile.get("column_details", []),
            "numerical_columns": profile.get("numerical_columns", []),
            "categorical_columns": profile.get("categorical_columns", []),
        },
        "detected_columns": detected_columns,
        "cleaning": {
            "original_rows": cleaning_result["original_rows"],
            "final_rows": cleaning_result["final_rows"],
            "duplicates_removed": cleaning_result["duplicates_removed"],
        },
        "kpis": kpis,
        "eda": eda_results,
        "charts": charts,
        "insights": insights,
        "recommendations": recommendations,
        "anomalies": anomalies,
    }

if __name__ == "__main__":

    result = run_pipeline("data/sample_sales.csv")

    print("\n===== SBI-ADS COMPLETE ANALYSIS =====")

    print("\nDataset:")
    print(result["profile"]["rows"], "rows /", result["profile"]["columns"], "columns")

    print("\nKPIs:")
    for name, value in result["kpis"].items():
        print(f"  {name}: {value}")

    print("\nInsights:")
    for insight in result["insights"]:
        print("-", insight)

    print("\nRecommendations:")
    for recommendation in result["recommendations"]:
        print("-", recommendation["recommendation"])

    print("\nAnomalies:")
    for anomaly in result["anomalies"]:
        print("-", anomaly["message"])

    print("\nCharts:")
    for chart in result["charts"]:
        print("-", chart)
