from __future__ import annotations

import numpy as np
import pandas as pd

from core import config

MIN_WEEKS = 6
ROBUST_Z_CONSTANT = 0.6745


def _detect_for_series(values: pd.Series, threshold: float) -> list[dict]:
    series = values.astype(float)
    median = float(series.median())
    mad = float((series - median).abs().median())

    if mad > 0:
        scores = ROBUST_Z_CONSTANT * (series - median) / mad
        expected = pd.Series(median, index=series.index)
    else:
        std = float(series.std())
        if std <= 0:
            return []
        scores = (series - series.mean()) / std
        expected = pd.Series(float(series.mean()), index=series.index)

    anomalies = []

    for week, score in scores.items():
        if abs(float(score)) < threshold:
            continue

        actual = float(series.loc[week])
        expected_value = float(expected.loc[week])
        deviation = actual - expected_value

        anomalies.append(
            {
                "week": str(week),
                "weekly_quantity": round(actual, 2),
                "expected_quantity": round(expected_value, 2),
                "deviation": round(deviation, 2),
                "score": round(float(score), 2),
                "severity": "High" if abs(float(score)) >= threshold * 1.5 else "Medium",
                "type": "Demand Spike" if deviation > 0 else "Demand Drop",
                "message": (
                    f"Week of {week}: demand of {actual:,.0f} units deviates "
                    f"by {abs(deviation):,.0f} from the normal level "
                    f"(robust z-score {float(score):.1f})."
                ),
            }
        )

    return anomalies


def detect_anomalies(
    file_path: str | None = None,
    column_mapping: dict | None = None,
    threshold: float | None = None,
) -> list[dict]:
    threshold = threshold if threshold is not None else config.ANOMALY_Z_THRESHOLD

    if file_path is not None and column_mapping is not None:
        from ml.uploaded_weekly_preparation import prepare_uploaded_weekly_data

        weekly = prepare_uploaded_weekly_data(file_path, column_mapping)
    else:
        from ml.weekly_preparation import prepare_weekly_data

        weekly = prepare_weekly_data()

    if weekly.empty or "Week" not in weekly.columns:
        return []

    anomalies = []

    for product, group in weekly.groupby("Product"):
        group = group.sort_values("Week")

        if len(group) < MIN_WEEKS:
            continue

        product_anomalies = _detect_for_series(
            group.set_index("Week")["Weekly_Quantity"], threshold
        )

        for anomaly in product_anomalies:
            anomaly["product"] = str(product)
            anomalies.append(anomaly)

    anomalies.sort(key=lambda item: abs(item["score"]), reverse=True)
    return anomalies

if __name__ == "__main__":

    print("===== SBI-ADS ANOMALY DETECTION =====")

    found = detect_anomalies()

    if not found:
        print("No anomalies detected in the default dataset.")
    else:
        for item in found:
            print(
                f"\n[{item['severity']}] {item['product']} — "
                f"{item['type']} ({item['week']})"
            )
            print(f"   {item['message']}")
