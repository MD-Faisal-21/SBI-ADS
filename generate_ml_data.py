import os

import numpy as np
import pandas as pd

RANDOM_SEED = 42

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

OUTPUT_PATH = "data/ml_sales_data.csv"

PRODUCTS = {

    "Laptop": {
        "category": "Electronics",
        "price": 55000,
        "base_demand": 8
    },

    "Monitor": {
        "category": "Electronics",
        "price": 12000,
        "base_demand": 14
    },

    "Keyboard": {
        "category": "Accessories",
        "price": 1500,
        "base_demand": 20
    },

    "Mouse": {
        "category": "Accessories",
        "price": 800,
        "base_demand": 28
    }

}

CUSTOMERS = [

    "Rahul",
    "Amit",
    "Neha",
    "Rohit",
    "Priya",
    "Sneha",
    "Arjun",
    "Vikas",
    "Pooja",
    "Karan"

]

REGIONS = [

    "Mumbai",
    "Pune",
    "Delhi",
    "Bangalore",
    "Hyderabad"

]

REGION_PROBABILITIES = [

    0.30,
    0.20,
    0.20,
    0.18,
    0.12

]

REGIONAL_FACTOR = {

    "Mumbai": 1.20,
    "Pune": 1.00,
    "Delhi": 1.05,
    "Bangalore": 0.95,
    "Hyderabad": 0.90

}

WEEKDAY_FACTOR = {

    0: 0.95,
    1: 1.00,
    2: 1.02,
    3: 1.05,
    4: 1.08,
    5: 1.15,
    6: 1.10

}

SEASONAL_FACTOR = {

    1: 0.90,
    2: 0.92,
    3: 0.98,
    4: 1.00,
    5: 1.02,
    6: 1.05,
    7: 1.04,
    8: 1.02,
    9: 1.08,
    10: 1.18,
    11: 1.25,
    12: 1.22

}


def generate_sales_dataset():

    np.random.seed(RANDOM_SEED)

    dates = pd.date_range(
        start=START_DATE,
        end=END_DATE,
        freq="D"
    )

    records = []

    for date in dates:

        day_number = (
            date - dates.min()
        ).days

        trend_factor = (
            1 + 0.30 * day_number / 364
        )

        weekday_factor = WEEKDAY_FACTOR[
            date.dayofweek
        ]

        seasonal_factor = SEASONAL_FACTOR[
            date.month
        ]

        for product_name, product in PRODUCTS.items():

            region = np.random.choice(
                REGIONS,
                p=REGION_PROBABILITIES
            )

            demand_noise = np.random.normal(
                loc=1.0,
                scale=0.03
            )

            expected_quantity = (

                product["base_demand"]

                * trend_factor

                * weekday_factor

                * seasonal_factor

                * REGIONAL_FACTOR[region]

                * demand_noise

            )

            quantity = max(
                1,
                int(
                    round(
                        expected_quantity
                    )
                )
            )

            customer = np.random.choice(
                CUSTOMERS
            )

            price = round(
                product["price"]
                * np.random.normal(
                    loc=1.0,
                    scale=0.02
                ),
                2
            )

            records.append({

                "Date":
                    date.strftime("%Y-%m-%d"),

                "Product":
                    product_name,

                "Category":
                    product["category"],

                "Quantity":
                    quantity,

                "Price":
                    price,

                "Customer":
                    customer,

                "Region":
                    region

            })

    return pd.DataFrame(records)


def validate_dataset(df):

    required_columns = [

        "Date",
        "Product",
        "Category",
        "Quantity",
        "Price",
        "Customer",
        "Region"

    ]

    missing_columns = [

        column
        for column in required_columns
        if column not in df.columns

    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    if df.empty:

        raise ValueError(
            "Generated dataset is empty."
        )

    if df["Quantity"].isnull().any():

        raise ValueError(
            "Quantity contains missing values."
        )

    if (df["Quantity"] < 1).any():

        raise ValueError(
            "Quantity must be greater than zero."
        )

    if df["Price"].isnull().any():

        raise ValueError(
            "Price contains missing values."
        )

    if (df["Price"] <= 0).any():

        raise ValueError(
            "Price must be greater than zero."
        )


def save_dataset(df, output_path=OUTPUT_PATH):

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:

        os.makedirs(
            output_directory,
            exist_ok=True
        )

    df.to_csv(
        output_path,
        index=False
    )


def display_dataset_summary(df, output_path=OUTPUT_PATH):

    print(
        "\n=============================================="
    )

    print(
        "        SBI-ADS ML DATASET GENERATOR"
    )

    print(
        "=============================================="
    )

    print(
        "\nDataset generated successfully!"
    )

    print(
        f"\nOutput file: {output_path}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"Unique dates: "
        f"{df['Date'].nunique()}"
    )

    print(
        f"Unique products: "
        f"{df['Product'].nunique()}"
    )

    print(
        f"Unique customers: "
        f"{df['Customer'].nunique()}"
    )

    print(
        f"Unique regions: "
        f"{df['Region'].nunique()}"
    )

    print(
        "\nProduct distribution:"
    )

    print(
        df["Product"].value_counts()
    )

    print(
        "\nFirst 10 records:"
    )

    print(
        df.head(10).to_string(
            index=False
        )
    )

    print(
        "\n=============================================="
    )


def main():

    dataset = generate_sales_dataset()

    validate_dataset(
        dataset
    )

    save_dataset(
        dataset,
        OUTPUT_PATH
    )

    display_dataset_summary(
        dataset,
        OUTPUT_PATH
    )

if __name__ == "__main__":

    main()
