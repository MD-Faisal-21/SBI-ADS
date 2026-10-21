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

from ml.weekly_preparation import prepare_weekly_data


def compare_weekly_models():

    df = prepare_weekly_data()

    features = [
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

    target = "Weekly_Quantity"

    unique_weeks = sorted(
        df["Week"].unique()
    )

    split_index = int(
        len(unique_weeks) * 0.80
    )

    training_weeks = unique_weeks[
        :split_index
    ]

    testing_weeks = unique_weeks[
        split_index:
    ]

    train_df = df[
        df["Week"].isin(
            training_weeks
        )
    ]

    test_df = df[
        df["Week"].isin(
            testing_weeks
        )
    ]

    X_train = train_df[features]

    X_test = test_df[features]

    y_train = train_df[target]

    y_test = test_df[target]

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
                n_estimators=300,
                max_depth=10,
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

    return results, len(training_weeks), len(testing_weeks)

if __name__ == "__main__":

    results, train_weeks, test_weeks = (
        compare_weekly_models()
    )

    print(
        "===== SBI-ADS WEEKLY DEMAND MODEL ====="
    )

    print(
        f"\nTraining weeks: {train_weeks}"
    )

    print(
        f"Testing weeks: {test_weeks}"
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
