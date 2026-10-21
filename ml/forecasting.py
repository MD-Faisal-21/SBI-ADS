import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from ml.data_preparation import prepare_sales_data


def compare_models():

    df = prepare_sales_data()

    features = [
        "Product",
        "TimeIndex",
        "Year",
        "Month",
        "Day",
        "DayOfWeek",
        "Quarter",
        "IsWeekend",
        "Lag_1",
        "Lag_7",
        "Lag_14",
        "Lag_28",
        "Rolling_7",
        "Rolling_14",
        "Rolling_30"
    ]

    target = "Daily_Quantity"

    X = df[features]

    y = df[target]

    split_index = int(
        len(df) * 0.80
    )

    X_train = X.iloc[:split_index]

    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]

    y_test = y.iloc[split_index:]

    categorical_features = [
        "Product"
    ]

    numerical_features = [
        feature
        for feature in features
        if feature not in categorical_features
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

    models = {

        "Linear Regression":
            LinearRegression(),

        "Random Forest":
            RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                random_state=42
            ),

        "Gradient Boosting":
            GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=42
            )

    }

    results = {}

    for name, model in models.items():

        pipeline = Pipeline(

            steps=[

                (
                    "preprocessor",
                    preprocessor
                ),

                (
                    "model",
                    model
                )

            ]

        )

        pipeline.fit(
            X_train,
            y_train
        )

        predictions = pipeline.predict(
            X_test
        )

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

        results[name] = {

            "model": pipeline,

            "mae":
                round(mae, 2),

            "rmse":
                round(rmse, 2),

            "r2":
                round(r2, 2)

        }

    return results

if __name__ == "__main__":

    results = compare_models()

    print(
        "===== SBI-ADS PRODUCT DEMAND MODEL ====="
    )

    print(
        "\nModel Performance:"
    )

    for name, result in results.items():

        print(
            f"\n{name}"
        )

        print(
            f"MAE: {result['mae']}"
        )

        print(
            f"RMSE: {result['rmse']}"
        )

        print(
            f"R² Score: {result['r2']}"
        )
