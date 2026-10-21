from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core import config

CHART_FOLDER = str(config.CHART_DIR)

COLOR_PRIMARY = "#4f46e5"
COLOR_ACCENT = "#06b6d4"
COLOR_NEUTRAL = "#64748b"
COLOR_TEXT = "#0f172a"
COLOR_GRID = "#e2e8f0"
SERIES_COLORS = [
    "#4f46e5", "#06b6d4", "#10b981", "#f59e0b",
    "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6",
]

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": COLOR_GRID,
        "axes.labelcolor": COLOR_TEXT,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlecolor": COLOR_TEXT,
        "axes.grid": True,
        "grid.color": COLOR_GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "font.size": 10,
        "text.color": COLOR_TEXT,
        "xtick.color": COLOR_NEUTRAL,
        "ytick.color": COLOR_NEUTRAL,
    }
)

os.makedirs(CHART_FOLDER, exist_ok=True)


def _style_axes(axis):
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)
    axis.spines["left"].set_color(COLOR_GRID)
    axis.spines["bottom"].set_color(COLOR_GRID)


def _bar_colors(count: int) -> list[str]:
    if count <= len(SERIES_COLORS):
        return SERIES_COLORS[:count]
    return [COLOR_PRIMARY] * count


def _save(current_figure, name: str, generated: list[str]) -> None:
    path = os.path.join(CHART_FOLDER, name)
    current_figure.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(current_figure)
    generated.append(path)


def generate_charts(df: pd.DataFrame, detected_columns: dict) -> list[str]:
    generated_charts = []

    column_by_type = {}
    for column, semantic_type in detected_columns.items():
        column_by_type.setdefault(semantic_type, column)

    product_column = column_by_type.get("product")
    quantity_column = column_by_type.get("quantity")
    price_column = column_by_type.get("unit_price")
    revenue_column = column_by_type.get("revenue")
    location_column = column_by_type.get("location")
    category_column = column_by_type.get("category")
    date_column = column_by_type.get("date")

    working = df.copy()

    if quantity_column and price_column:
        working["_revenue"] = (
            pd.to_numeric(working[quantity_column], errors="coerce")
            * pd.to_numeric(working[price_column], errors="coerce")
        )
    elif revenue_column:
        working["_revenue"] = pd.to_numeric(working[revenue_column], errors="coerce")
    elif quantity_column:
        working["_revenue"] = pd.to_numeric(working[quantity_column], errors="coerce")
    else:
        working["_revenue"] = 0

    if product_column and (quantity_column or "_revenue" in working):
        metric = "_revenue" if "_revenue" in working else quantity_column
        label = "Revenue" if metric == "_revenue" else "Quantity Sold"

        product_data = (
            working.groupby(product_column)[metric]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        figure, axis = plt.subplots(figsize=(8, 5))
        axis.barh(product_data.index.astype(str)[::-1], product_data.values[::-1],
                  color=_bar_colors(len(product_data)))
        axis.set_title("Top Products by " + label)
        axis.set_xlabel(label)
        _style_axes(axis)
        figure.tight_layout()
        _save(figure, "product_performance.png", generated_charts)

    if location_column and (quantity_column or "_revenue" in working):
        metric = "_revenue" if "_revenue" in working else quantity_column
        label = "Revenue" if metric == "_revenue" else "Quantity Sold"

        location_data = (
            working.groupby(location_column)[metric]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        figure, axis = plt.subplots(figsize=(8, 5))
        axis.bar(location_data.index.astype(str), location_data.values,
                 color=COLOR_ACCENT)
        axis.set_title(label + " by Region")
        axis.set_xlabel("Region")
        axis.set_ylabel(label)
        plt.setp(axis.get_xticklabels(), rotation=30, ha="right")
        _style_axes(axis)
        figure.tight_layout()
        _save(figure, "regional_performance.png", generated_charts)

    if price_column:
        prices = pd.to_numeric(working[price_column], errors="coerce").dropna()

        if not prices.empty:
            figure, axis = plt.subplots(figsize=(8, 5))
            axis.hist(prices, bins=20, color=COLOR_PRIMARY,
                      alpha=0.85, edgecolor="white")
            axis.axvline(prices.median(), color=COLOR_ACCENT, linestyle="--",
                         linewidth=1.5, label=f"Median: {prices.median():,.0f}")
            axis.set_title("Price Distribution")
            axis.set_xlabel("Price")
            axis.set_ylabel("Frequency")
            axis.legend(frameon=False)
            _style_axes(axis)
            figure.tight_layout()
            _save(figure, "price_distribution.png", generated_charts)

    numeric_df = working.select_dtypes(include="number")
    numeric_df = numeric_df.loc[:, numeric_df.std() > 0]

    if numeric_df.shape[1] > 1:
        correlation = numeric_df.corr()
        figure, axis = plt.subplots(figsize=(7.5, 5.5))

        image = axis.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1,
                            aspect="auto")
        figure.colorbar(image, ax=axis, shrink=0.8)

        axis.set_xticks(range(len(correlation.columns)))
        axis.set_xticklabels(correlation.columns, rotation=45, ha="right")
        axis.set_yticks(range(len(correlation.index)))
        axis.set_yticklabels(correlation.index)
        axis.grid(False)

        for i in range(len(correlation)):
            for j in range(len(correlation.columns)):
                value = correlation.iloc[i, j]
                axis.text(
                    j, i, f"{value:.2f}",
                    ha="center", va="center", fontsize=8,
                    color="white" if abs(value) > 0.6 else COLOR_TEXT,
                )

        axis.set_title("Correlation Analysis")
        figure.tight_layout()
        _save(figure, "correlation_heatmap.png", generated_charts)

    if date_column and (quantity_column or "_revenue" in working):
        metric = "_revenue" if "_revenue" in working else quantity_column
        label = "Revenue" if metric == "_revenue" else "Quantity Sold"

        date_data = working.copy()
        date_data[date_column] = pd.to_datetime(
            date_data[date_column], errors="coerce"
        )
        date_data = date_data.dropna(subset=[date_column])

        if not date_data.empty:
            trend = (
                date_data.groupby(date_data[date_column].dt.date)[metric]
                .sum()
                .sort_index()
            )

            figure, axis = plt.subplots(figsize=(10, 5))
            axis.plot(trend.index, trend.values, color=COLOR_PRIMARY,
                      linewidth=1.4, alpha=0.45, label="Daily")

            if len(trend) >= 7:
                rolling = trend.rolling(7).mean()
                axis.plot(rolling.index, rolling.values, color=COLOR_ACCENT,
                          linewidth=2.4, label="7-day average")

            axis.set_title(label + " Trend Over Time")
            axis.set_xlabel("Date")
            axis.set_ylabel(label)
            axis.legend(frameon=False)
            plt.setp(axis.get_xticklabels(), rotation=30, ha="right")
            _style_axes(axis)
            figure.tight_layout()
            _save(figure, "sales_trend.png", generated_charts)

    return generated_charts

if __name__ == "__main__":

    from analytics.column_detector import detect_columns
    from analytics.data_cleaner import clean_dataset

    cleaning_result = clean_dataset("data/sample_sales.csv")
    detected_columns = detect_columns(cleaning_result["cleaned_data"])

    charts = generate_charts(cleaning_result["cleaned_data"], detected_columns)

    print("\n===== GENERATED CHARTS =====")
    for chart in charts:
        print(chart)
