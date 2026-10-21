import pandas as pd


def prepare_weekly_data(
    file_path="data/ml_sales_data.csv"
):

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    df["Week"] = (
        df["Date"]
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    week_counts = (
        df.groupby("Week")["Date"]
        .nunique()
    )

    complete_weeks = week_counts[
        week_counts == 7
    ].index

    df = df[
        df["Week"].isin(
            complete_weeks
        )
    ]

    weekly_sales = (
        df.groupby(
            ["Week", "Product"]
        )["Quantity"]
        .sum()
        .reset_index()
    )

    weekly_sales.rename(
        columns={
            "Quantity":
                "Weekly_Quantity"
        },
        inplace=True
    )

    all_weeks = pd.date_range(
        start=weekly_sales["Week"].min(),
        end=weekly_sales["Week"].max(),
        freq="7D"
    )

    all_products = df["Product"].unique()

    complete_index = pd.MultiIndex.from_product(
        [all_weeks, all_products],
        names=["Week", "Product"]
    )

    weekly_sales = (
        weekly_sales
        .set_index(
            ["Week", "Product"]
        )
        .reindex(
            complete_index,
            fill_value=0
        )
        .reset_index()
    )

    weekly_sales = weekly_sales.sort_values(
        ["Product", "Week"]
    )

    weekly_sales["TimeIndex"] = (
        weekly_sales
        .groupby("Product")
        .cumcount()
    )

    weekly_sales["Year"] = (
        weekly_sales["Week"].dt.year
    )

    weekly_sales["Month"] = (
        weekly_sales["Week"].dt.month
    )

    weekly_sales["Quarter"] = (
        weekly_sales["Week"].dt.quarter
    )

    weekly_sales["WeekOfYear"] = (
        weekly_sales["Week"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    weekly_sales["Lag_1"] = (
        weekly_sales
        .groupby("Product")["Weekly_Quantity"]
        .shift(1)
    )

    weekly_sales["Lag_2"] = (
        weekly_sales
        .groupby("Product")["Weekly_Quantity"]
        .shift(2)
    )

    weekly_sales["Lag_4"] = (
        weekly_sales
        .groupby("Product")["Weekly_Quantity"]
        .shift(4)
    )

    weekly_sales["Lag_8"] = (
        weekly_sales
        .groupby("Product")["Weekly_Quantity"]
        .shift(8)
    )

    weekly_sales["Rolling_4"] = (
        weekly_sales
        .groupby("Product")["Weekly_Quantity"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(4)
            .mean()
        )
    )

    weekly_sales["Rolling_8"] = (
        weekly_sales
        .groupby("Product")["Weekly_Quantity"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(8)
            .mean()
        )
    )

    weekly_sales = weekly_sales.dropna()

    return weekly_sales

if __name__ == "__main__":

    data = prepare_weekly_data()

    print(
        "===== WEEKLY PRODUCT ML DATA ====="
    )

    print(
        f"Rows: {len(data)}"
    )

    print(
        f"Columns: {len(data.columns)}"
    )

    print(
        "\nPrepared Data:"
    )

    print(
        data.head(15)
    )

    print(
        "\nProducts:"
    )

    print(
        data["Product"].unique()
    )

    print(
        "\nDate range:"
    )

    print(
        data["Week"].min(),
        "to",
        data["Week"].max()
    )

    print(
        "\nColumns:"
    )

    print(
        list(data.columns)
    )
