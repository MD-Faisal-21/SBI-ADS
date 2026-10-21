from __future__ import annotations

import pandas as pd


def generate_insights(df, kpis, eda_results, detected_columns):
    insights = []

    column_by_type = {}
    for column, semantic_type in detected_columns.items():
        column_by_type.setdefault(semantic_type, column)

    product_column = column_by_type.get("product")
    quantity_column = column_by_type.get("quantity")
    location_column = column_by_type.get("location")
    date_column = column_by_type.get("date")

    total_revenue = kpis.get("total_revenue")

    if product_column and quantity_column:

        product_quantity = (
            df.groupby(product_column)[quantity_column]
            .sum()
            .sort_values(ascending=False)
        )

        if not product_quantity.empty:

            top_product = product_quantity.index[0]
            top_quantity = product_quantity.iloc[0]
            total_quantity = product_quantity.sum()

            if total_quantity > 0:
                percentage = (top_quantity / total_quantity) * 100

                if percentage >= 40:
                    insights.append(
                        f"{top_product} accounts for {percentage:.1f}% of total "
                        "quantity sold, indicating strong product concentration."
                    )
                else:
                    insights.append(
                        f"{top_product} is the highest-selling product by "
                        "quantity in the dataset."
                    )

    if product_column and total_revenue and kpis.get("top_product"):

        top_share = ""
        if kpis.get("top_product_revenue") and total_revenue:
            share = (kpis["top_product_revenue"] / total_revenue) * 100
            top_share = f" — {share:.1f}% of total revenue"

        insights.append(
            f"{kpis['top_product']} leads revenue with "
            f"{kpis.get('top_product_revenue', 0):,.0f} in sales{top_share}."
        )

    if location_column and quantity_column:

        location_quantity = (
            df.groupby(location_column)[quantity_column]
            .sum()
            .sort_values(ascending=False)
        )

        if not location_quantity.empty and location_quantity.sum() > 0:

            top_location = location_quantity.index[0]
            percentage = (
                location_quantity.iloc[0] / location_quantity.sum()
            ) * 100

            insights.append(
                f"{top_location} is the highest-volume location, contributing "
                f"approximately {percentage:.1f}% of total quantity."
            )

    correlations = eda_results.get("correlations", {})

    if quantity_column:

        for column, values in correlations.items():

            if column == quantity_column:
                continue

            if quantity_column in values:

                correlation = values[quantity_column]

                if correlation <= -0.5:
                    insights.append(
                        f"There is a negative relationship between "
                        f"{quantity_column} and {column} "
                        f"(correlation: {correlation:.2f})."
                    )
                elif correlation >= 0.5:
                    insights.append(
                        f"There is a positive relationship between "
                        f"{quantity_column} and {column} "
                        f"(correlation: {correlation:.2f})."
                    )

    if kpis.get("period_start") and kpis.get("period_end"):
        insights.append(
            f"The dataset covers the period from {kpis['period_start']} "
            f"to {kpis['period_end']}."
        )

    duplicate_rows = int(df.duplicated().sum())

    if duplicate_rows == 0:
        insights.append("No duplicate records were detected in the analyzed dataset.")
    else:
        insights.append(
            f"{duplicate_rows} duplicate records were detected and removed "
            "during cleaning."
        )

    return insights

if __name__ == "__main__":

    from analytics.column_detector import detect_columns
    from analytics.data_cleaner import clean_dataset
    from analytics.eda_engine import perform_eda
    from analytics.kpi_engine import calculate_kpis

    cleaning_result = clean_dataset("data/sample_sales.csv")
    df = cleaning_result["cleaned_data"]
    detected_columns = detect_columns(df)

    kpis = calculate_kpis(df, detected_columns)
    eda_results = perform_eda(df, detected_columns)

    insights = generate_insights(df, kpis, eda_results, detected_columns)

    print("\n===== SBI-ADS BUSINESS INSIGHTS =====")
    for number, insight in enumerate(insights, start=1):
        print(f"{number}. {insight}")
