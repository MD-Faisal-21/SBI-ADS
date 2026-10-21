import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

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


def train_final_model(
    df=None
):

    if df is None:

        df = prepare_weekly_data()

    X = df[FEATURES]

    y = df["Weekly_Quantity"]

    categorical_features = [
        "Product"
    ]

    numerical_features = [
        feature
        for feature in FEATURES
        if feature != "Product"
    ]

    preprocessor = ColumnTransformer(

        transformers=[

            (
                "product",

                OneHotEncoder(
                    handle_unknown="ignore"
                ),

                categorical_features
            ),

            (
                "numerical",

                "passthrough",

                numerical_features
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
        X,
        y
    )

    return model, df


def generate_forecast(
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

    model, df = train_final_model(
        df
    )

    latest_rows = (
        df
        .sort_values(
            ["Product", "Week"]
        )
        .groupby("Product")
        .tail(1)
        .copy()
    )

    predictions = model.predict(
        latest_rows[FEATURES]
    )

    predictions = [
        max(
            0,
            prediction
        )
        for prediction in predictions
    ]

    forecast = pd.DataFrame({

        "Product":
            latest_rows[
                "Product"
            ].values,

        "Last_Week":
            latest_rows[
                "Week"
            ].values,

        "Current_Weekly_Demand":
            latest_rows[
                "Weekly_Quantity"
            ].values,

        "Predicted_Next_Week":
            [
                round(
                    value,
                    2
                )
                for value in predictions
            ]

    })

    forecast["Demand_Change"] = (

        forecast[
            "Predicted_Next_Week"
        ]

        -

        forecast[
            "Current_Weekly_Demand"
        ]

    ).round(2)

    forecast[
        "Demand_Change_Percent"
    ] = (

        (
            forecast[
                "Demand_Change"
            ]

            /

            forecast[
                "Current_Weekly_Demand"
            ]
        )

        * 100

    ).replace(

        [
            float("inf"),
            -float("inf")
        ],

        0

    ).fillna(0).round(2)

    forecast["Trend"] = (

        forecast[
            "Demand_Change"
        ]

        .apply(

            lambda x:

            "Increasing"
            if x > 0

            else

            "Decreasing"
            if x < 0

            else

            "Stable"

        )

    )

    return forecast

if __name__ == "__main__":

    forecast = generate_forecast()

    print(
        "===== SBI-ADS DEMAND FORECAST ====="
    )

    print(
        "\nNext Week Forecast:"
    )

    print(
        forecast.to_string(
            index=False
        )
    )
