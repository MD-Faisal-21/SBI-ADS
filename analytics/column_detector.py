COLUMN_PATTERNS = {

    "date": [
        "date",
        "order_date",
        "transaction_date",
        "purchase_date",
        "orderdate",
        "transactiondate",
        "timestamp"
    ],

    "product": [
        "product",
        "product_name",
        "productname",
        "item",
        "item_name",
        "itemname"
    ],

    "category": [
        "category",
        "product_category",
        "type",
        "segment"
    ],

    "quantity": [
        "quantity",
        "qty",
        "units",
        "units_sold",
        "quantity_sold",
        "units_purchased"
    ],

    "unit_price": [
        "price",
        "unit_price",
        "selling_price",
        "unitprice",
        "sellingprice"
    ],

    "revenue": [
        "revenue",
        "sales",
        "sales_amount",
        "total_sales",
        "total_revenue",
        "revenue_amount",
        "sales_value"
    ],

    "cost": [
        "cost",
        "unit_cost",
        "purchase_cost",
        "cost_price",
        "total_cost"
    ],

    "profit": [
        "profit",
        "profit_amount",
        "net_profit",
        "gross_profit"
    ],

    "customer": [
        "customer",
        "customer_name",
        "customername",
        "client",
        "client_name",
        "clientname"
    ],

    "location": [
        "region",
        "city",
        "location",
        "state",
        "country",
        "area"
    ]
}


def normalize_column_name(column_name):

    return (
        str(column_name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def detect_columns(df):

    detected_columns = {}

    for column in df.columns:

        normalized_name = normalize_column_name(
            column
        )

        detected_type = "unknown"

        for semantic_type, patterns in COLUMN_PATTERNS.items():

            if normalized_name in patterns:

                detected_type = semantic_type
                break

        if detected_type == "unknown":

            if (
                "date" in normalized_name
                or "time" in normalized_name
            ):
                detected_type = "date"

        detected_columns[column] = detected_type

    return detected_columns

if __name__ == "__main__":

    import pandas as pd

    df = pd.read_csv(
        "data/sample_sales.csv"
    )

    detected = detect_columns(df)

    print("Detected Columns:\n")

    for column, semantic_type in detected.items():

        print(
            f"{column} → {semantic_type}"
        )
