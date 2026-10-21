def generate_recommendations(
    df,
    kpis,
    eda_results,
    detected_columns
):

    recommendations = []

    product_column = None
    quantity_column = None
    location_column = None

    for column, semantic_type in detected_columns.items():

        if semantic_type == "product":
            product_column = column

        elif semantic_type == "quantity":
            quantity_column = column

        elif semantic_type == "location":
            location_column = column

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

            percentage = (
                top_quantity / total_quantity
            ) * 100

            if percentage >= 40:

                recommendations.append({
                    "area": "Inventory",
                    "priority": "High",
                    "recommendation":
                        f"Consider maintaining adequate "
                        f"inventory levels for {top_product} "
                        "because it represents a high share "
                        "of total quantity sold."
                })

    if location_column and quantity_column:

        location_quantity = (
            df.groupby(location_column)[quantity_column]
            .sum()
            .sort_values(ascending=False)
        )

        if len(location_quantity) >= 2:

            top_location = location_quantity.index[0]
            lowest_location = location_quantity.index[-1]

            top_value = location_quantity.iloc[0]
            lowest_value = location_quantity.iloc[-1]

            if top_value > lowest_value * 2:

                recommendations.append({
                    "area": "Regional Performance",
                    "priority": "Medium",
                    "recommendation":
                        f"{top_location} shows significantly "
                        f"higher activity than {lowest_location}. "
                        f"Consider investigating the factors "
                        f"behind the performance difference."
                })

    correlations = eda_results.get(
        "correlations",
        {}
    )

    if quantity_column:

        for column, values in correlations.items():

            if column == quantity_column:
                continue

            if quantity_column in values:

                correlation = values[quantity_column]

                if correlation <= -0.5:

                    recommendations.append({
                        "area": "Pricing",
                        "priority": "Medium",
                        "recommendation":
                            f"The data shows a negative "
                            f"relationship between quantity "
                            f"and {column}. Consider reviewing "
                            "pricing and demand patterns before "
                            "making pricing decisions."
                    })

    if not recommendations:

        recommendations.append({
            "area": "General",
            "priority": "Low",
            "recommendation":
                "No major decision-support recommendations "
                "were identified from the current dataset."
        })

    return recommendations

if __name__ == "__main__":

    import pandas as pd

    from analytics.column_detector import detect_columns
    from analytics.data_cleaner import clean_dataset
    from analytics.kpi_engine import calculate_kpis
    from analytics.eda_engine import perform_eda

    cleaning_result = clean_dataset(
        "data/sample_sales.csv"
    )

    df = cleaning_result["cleaned_data"]

    detected_columns = detect_columns(df)

    kpis = calculate_kpis(
        df,
        detected_columns
    )

    eda_results = perform_eda(
        df,
        detected_columns
    )

    recommendations = generate_recommendations(
        df,
        kpis,
        eda_results,
        detected_columns
    )

    print("\n===== SBI-ADS DECISION SUPPORT =====")

    for number, item in enumerate(
        recommendations,
        start=1
    ):

        print(f"\n{number}. Area: {item['area']}")
        print(f"   Priority: {item['priority']}")
        print(
            f"   Recommendation: "
            f"{item['recommendation']}"
        )
