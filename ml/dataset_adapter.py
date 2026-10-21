import pandas as pd


def prepare_uploaded_dataset(
    file_path,
    column_mapping
):

    if file_path.lower().endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    required = [
        "date",
        "product",
        "quantity"
    ]

    detected = set(
        column_mapping.values()
    )

    missing = [
        column
        for column in required
        if column not in detected
    ]

    if missing:
        raise ValueError(
            "Dataset does not contain the required "
            "columns for demand forecasting: "
            + ", ".join(missing)
        )

    date_column = next(
        column
        for column, normalized in column_mapping.items()
        if normalized == "date"
    )

    product_column = next(
        column
        for column, normalized in column_mapping.items()
        if normalized == "product"
    )

    quantity_column = next(
        column
        for column, normalized in column_mapping.items()
        if normalized == "quantity"
    )

    ml_df = df[
        [
            date_column,
            product_column,
            quantity_column
        ]
    ].copy()

    ml_df.columns = [
        "Date",
        "Product",
        "Quantity"
    ]

    ml_df["Date"] = pd.to_datetime(
        ml_df["Date"],
        errors="coerce"
    )

    ml_df["Quantity"] = pd.to_numeric(
        ml_df["Quantity"],
        errors="coerce"
    )

    ml_df = ml_df.dropna(
        subset=[
            "Date",
            "Product",
            "Quantity"
        ]
    )

    ml_df = ml_df[
        ml_df["Quantity"] >= 0
    ]

    return ml_df


def check_ml_compatibility(
    file_path,
    column_mapping
):

    try:

        ml_df = prepare_uploaded_dataset(
            file_path,
            column_mapping
        )

        if len(ml_df) == 0:

            return {
                "compatible": False,
                "reason":
                    "No valid date, product, and quantity records found."
            }

        unique_dates = (
            ml_df["Date"].nunique()
        )

        unique_products = (
            ml_df["Product"].nunique()
        )

        if unique_dates < 30:

            return {
                "compatible": False,
                "reason":
                    "At least 30 unique dates are recommended for demand forecasting."
            }

        if unique_products == 0:

            return {
                "compatible": False,
                "reason":
                    "No products were detected."
            }

        return {
            "compatible": True,
            "reason":
                "Dataset is suitable for demand forecasting.",
            "rows": len(ml_df),
            "unique_dates": unique_dates,
            "unique_products": unique_products
        }

    except Exception as error:

        return {
            "compatible": False,
            "reason": str(error)
        }

if __name__ == "__main__":

    print(
        "===== ML DATASET COMPATIBILITY ====="
    )

    print(
        "Adapter module loaded successfully."
    )
