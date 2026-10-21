import pandas as pd


def perform_eda(df, detected_columns):

    results = {
        "numerical_summary": {},
        "categorical_summary": {},
        "correlations": {},
        "date_analysis": {}
    }

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numerical_columns:

        results["numerical_summary"][column] = {
            "mean": round(float(df[column].mean()), 2),
            "median": round(float(df[column].median()), 2),
            "minimum": float(df[column].min()),
            "maximum": float(df[column].max()),
            "standard_deviation": round(
                float(df[column].std()),
                2
            )
        }

    categorical_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in categorical_columns:

        value_counts = (
            df[column]
            .value_counts()
            .head(10)
            .to_dict()
        )

        results["categorical_summary"][column] = {
            str(key): int(value)
            for key, value in value_counts.items()
        }

    if len(numerical_columns) > 1:

        correlation_matrix = (
            df[numerical_columns]
            .corr()
            .round(2)
        )

        results["correlations"] = (
            correlation_matrix
            .to_dict()
        )

    date_column = None

    for column, semantic_type in detected_columns.items():

        if semantic_type == "date":
            date_column = column
            break

    if date_column:

        date_series = pd.to_datetime(
            df[date_column],
            errors="coerce"
        )

        valid_dates = date_series.dropna()

        if not valid_dates.empty:

            results["date_analysis"] = {
                "start_date": str(
                    valid_dates.min().date()
                ),
                "end_date": str(
                    valid_dates.max().date()
                ),
                "number_of_days": int(
                    (valid_dates.max() -
                    valid_dates.min()).days + 1
                )
            }

    return results

if __name__ == "__main__":

    from analytics.column_detector import detect_columns
    from analytics.data_cleaner import clean_dataset

    cleaning_result = clean_dataset(
        "data/sample_sales.csv"
    )

    df = cleaning_result["cleaned_data"]

    detected_columns = detect_columns(df)

    eda_results = perform_eda(
        df,
        detected_columns
    )

    print("\n===== SBI-ADS EDA =====")

    print("\nNumerical Analysis:")

    for column, values in (
        eda_results["numerical_summary"].items()
    ):
        print(f"\n{column}:")
        print(values)

    print("\nCategorical Analysis:")

    for column, values in (
        eda_results["categorical_summary"].items()
    ):
        print(f"\n{column}:")
        print(values)

    print("\nCorrelations:")

    print(
        eda_results["correlations"]
    )

    print("\nDate Analysis:")

    print(
        eda_results["date_analysis"]
    )
