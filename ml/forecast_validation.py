import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from ml.weekly_preparation import prepare_weekly_data

from ml.uploaded_weekly_preparation import (
    prepare_uploaded_weekly_data
)

FEATURES = [

    "Product",
    "TimeIndex",
    "Year",
    "Month",
    "Quarter",
    "WeekOfYear",
    "Lag_1",
    "Lag_2",
    "Lag_4",
    "Lag_8",
    "Rolling_4",
    "Rolling_8"

]


def validate_model(
    file_path=None,
    column_mapping=None
):

    if (
        file_path is not None
        and column_mapping is not None
    ):

        df = prepare_uploaded_weekly_data(
            file_path,
            column_mapping
        )

    else:

        df = prepare_weekly_data()

    unique_weeks = sorted(
        df["Week"].unique()
    )

    split_index = int(
        len(unique_weeks) * 0.80
    )

    train_weeks = unique_weeks[
        :split_index
    ]

    test_weeks = unique_weeks[
        split_index:
    ]

    train_df = df[
        df["Week"].isin(
            train_weeks
        )
    ]

    test_df = df[
        df["Week"].isin(
            test_weeks
        )
    ]

    X_train = train_df[FEATURES]

    y_train = train_df[
        "Weekly_Quantity"
    ]

    X_test = test_df[FEATURES]

    y_test = test_df[
        "Weekly_Quantity"
    ]

    preprocessor = ColumnTransformer(

        transformers=[

            (
                "product",

                OneHotEncoder(
                    handle_unknown="ignore"
                ),

                ["Product"]

            ),

            (
                "numerical",

                "passthrough",

                [
                    feature
                    for feature in FEATURES
                    if feature != "Product"
                ]

            )

        ]

    )

    model = Pipeline(

        steps=[

            (
                "preprocessor",
                preprocessor
            ),

            (
                "model",
                LinearRegression()
            )

        ]

    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    predictions = [
        max(0, prediction)
        for prediction in predictions
    ]

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    comparison = test_df[
        [
            "Week",
            "Product",
            "Weekly_Quantity"
        ]
    ].copy()

    comparison[
        "Predicted_Quantity"
    ] = [
        round(value, 2)
        for value in predictions
    ]

    comparison[
        "Absolute_Error"
    ] = (

        comparison["Weekly_Quantity"]
        -
        comparison["Predicted_Quantity"]

    ).abs().round(2)

    return (
        model,
        comparison,
        mae,
        rmse,
        r2,
        len(train_weeks),
        len(test_weeks)
    )

if __name__ == "__main__":

    (
        model,
        comparison,
        mae,
        rmse,
        r2,
        train_weeks,
        test_weeks
    ) = validate_model()

    print(
        "===== SBI-ADS FORECAST VALIDATION ====="
    )

    print(
        f"\nTraining weeks: "
        f"{train_weeks}"
    )

    print(
        f"Testing weeks: "
        f"{test_weeks}"
    )

    print(
        "\nValidation Metrics:"
    )

    print(
        f"MAE: {mae:.2f}"
    )

    print(
        f"RMSE: {rmse:.2f}"
    )

    print(
        f"R² Score: {r2:.2f}"
    )

    print(
        "\nActual vs Predicted:"
    )

    print(
        comparison.to_string(
            index=False
        )
    )

    print(
        "\nProduct-Level Performance:"
    )

    for product in comparison["Product"].unique():

        product_data = comparison[
            comparison["Product"] == product
        ]

        product_mae = mean_absolute_error(
            product_data["Weekly_Quantity"],
            product_data["Predicted_Quantity"]
        )

        product_rmse = mean_squared_error(
            product_data["Weekly_Quantity"],
            product_data["Predicted_Quantity"]
        ) ** 0.5

        product_r2 = r2_score(
            product_data["Weekly_Quantity"],
            product_data["Predicted_Quantity"]
        )

        print(
            f"\n{product}"
        )

        print(
            f"MAE: {product_mae:.2f}"
        )

        print(
            f"RMSE: {product_rmse:.2f}"
        )

        print(
            f"R² Score: {product_r2:.2f}"
        )
