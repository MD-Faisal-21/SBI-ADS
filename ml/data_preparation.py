import pandas as pd


def prepare_sales_data(
    file_path="data/ml_sales_data.csv"
):

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    daily_sales = (
        df.groupby(
            ["Date", "Product"]
        )["Quantity"]
        .sum()
        .reset_index()
    )

    daily_sales.rename(
        columns={
            "Quantity": "Daily_Quantity"
        },
        inplace=True
    )

    all_dates = pd.date_range(
        start=df["Date"].min(),
        end=df["Date"].max(),
        freq="D"
    )

    all_products = df["Product"].unique()

    complete_index = pd.MultiIndex.from_product(
        [all_dates, all_products],
        names=["Date", "Product"]
    )

    daily_sales = (
        daily_sales
        .set_index(["Date", "Product"])
        .reindex(complete_index, fill_value=0)
        .reset_index()
    )

    daily_sales = daily_sales.sort_values(
        ["Product", "Date"]
    )

    daily_sales["TimeIndex"] = (
        daily_sales
        .groupby("Product")
        .cumcount()
    )

    daily_sales["Year"] = (
        daily_sales["Date"].dt.year
    )

    daily_sales["Month"] = (
        daily_sales["Date"].dt.month
    )

    daily_sales["Day"] = (
        daily_sales["Date"].dt.day
    )

    daily_sales["DayOfWeek"] = (
        daily_sales["Date"].dt.dayofweek
    )

    daily_sales["Quarter"] = (
        daily_sales["Date"].dt.quarter
    )

    daily_sales["IsWeekend"] = (
        daily_sales["DayOfWeek"] >= 5
    ).astype(int)

    daily_sales["Lag_1"] = (
        daily_sales
        .groupby("Product")["Daily_Quantity"]
        .shift(1)
    )

    daily_sales["Lag_7"] = (
        daily_sales
        .groupby("Product")["Daily_Quantity"]
        .shift(7)
    )

    daily_sales["Lag_14"] = (
        daily_sales
        .groupby("Product")["Daily_Quantity"]
        .shift(14)
    )

    daily_sales["Lag_28"] = (
        daily_sales
        .groupby("Product")["Daily_Quantity"]
        .shift(28)
    )

    daily_sales["Rolling_7"] = (
        daily_sales
        .groupby("Product")["Daily_Quantity"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(7)
            .mean()
        )
    )

    daily_sales["Rolling_14"] = (
        daily_sales
        .groupby("Product")["Daily_Quantity"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(14)
            .mean()
        )
    )

    daily_sales["Rolling_30"] = (
        daily_sales
        .groupby("Product")["Daily_Quantity"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(30)
            .mean()
        )
    )

    daily_sales = daily_sales.dropna()

    return daily_sales

if __name__ == "__main__":

    data = prepare_sales_data()

    print(
        "===== PRODUCT-LEVEL ML DATA ====="
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
        data["Date"].min(),
        "to",
        data["Date"].max()
    )

    print(
        "\nColumns:"
    )

    print(
        list(data.columns)
    )
