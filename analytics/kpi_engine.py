from __future__ import annotations

import pandas as pd


def calculate_kpis(df: pd.DataFrame, detected_columns: dict) -> dict:
    kpis = {}

    column_by_type = {}
    for column, semantic_type in detected_columns.items():
        column_by_type.setdefault(semantic_type, column)

    quantity_column = column_by_type.get("quantity")
    price_column = column_by_type.get("unit_price")
    revenue_column = column_by_type.get("revenue")
    cost_column = column_by_type.get("cost")
    profit_column = column_by_type.get("profit")
    product_column = column_by_type.get("product")
    customer_column = column_by_type.get("customer")
    location_column = column_by_type.get("location")
    category_column = column_by_type.get("category")
    date_column = column_by_type.get("date")

    quantity = (
        pd.to_numeric(df[quantity_column], errors="coerce")
        if quantity_column
        else None
    )
    price = (
        pd.to_numeric(df[price_column], errors="coerce")
        if price_column
        else None
    )

    if quantity is not None and price is not None:
        revenue_series = (quantity * price).fillna(0)
        kpis["total_revenue"] = float(revenue_series.sum())
    elif revenue_column:
        revenue_series = pd.to_numeric(df[revenue_column], errors="coerce").fillna(0)
        kpis["total_revenue"] = float(revenue_series.sum())
    else:
        revenue_series = None

    if quantity is not None:
        kpis["total_quantity"] = int(quantity.sum(skipna=True))

    if profit_column:
        profit_series = pd.to_numeric(df[profit_column], errors="coerce")
        kpis["total_profit"] = round(float(profit_series.sum(skipna=True)), 2)
    elif cost_column and revenue_series is not None:
        cost_series = pd.to_numeric(df[cost_column], errors="coerce")
        kpis["total_profit"] = round(
            float(revenue_series.sum() - cost_series.fillna(0).sum()), 2
        )

    if product_column:
        kpis["total_products"] = int(df[product_column].nunique())

    if customer_column:
        kpis["total_customers"] = int(df[customer_column].nunique())

    if location_column:
        kpis["total_locations"] = int(df[location_column].nunique())

    if price is not None:
        kpis["average_price"] = round(float(price.mean(skipna=True)), 2)

    if revenue_series is not None and len(df) > 0:
        kpis["average_order_value"] = round(float(revenue_series.mean()), 2)

    if product_column and revenue_series is not None:
        product_sales = (
            df.assign(_rev=revenue_series)
            .groupby(product_column)["_rev"]
            .sum()
            .sort_values(ascending=False)
        )
        if not product_sales.empty:
            kpis["top_product"] = str(product_sales.index[0])
            kpis["top_product_revenue"] = round(float(product_sales.iloc[0]), 2)

    if location_column and revenue_series is not None:
        location_sales = (
            df.assign(_rev=revenue_series)
            .groupby(location_column)["_rev"]
            .sum()
            .sort_values(ascending=False)
        )
        if not location_sales.empty:
            kpis["top_location"] = str(location_sales.index[0])

    if category_column and revenue_series is not None:
        category_sales = (
            df.assign(_rev=revenue_series)
            .groupby(category_column)["_rev"]
            .sum()
            .sort_values(ascending=False)
        )
        if not category_sales.empty:
            kpis["top_category"] = str(category_sales.index[0])

    if date_column:
        dates = pd.to_datetime(df[date_column], errors="coerce").dropna()
        if not dates.empty:
            kpis["period_start"] = str(dates.min().date())
            kpis["period_end"] = str(dates.max().date())

    return kpis

if __name__ == "__main__":

    from analytics.column_detector import detect_columns
    from analytics.data_cleaner import clean_dataset

    cleaning_result = clean_dataset("data/sample_sales.csv")
    detected = detect_columns(cleaning_result["cleaned_data"])

    kpis = calculate_kpis(cleaning_result["cleaned_data"], detected)

    print("\n===== SBI-ADS KPIs =====")
    for name, value in kpis.items():
        print(f"{name}: {value}")
