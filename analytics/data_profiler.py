import pandas as pd


def profile_dataset(file_path):

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)

    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)

    else:
        raise ValueError("Only CSV and Excel files are supported.")

    rows = len(df)
    columns = len(df.columns)

    column_details = []

    for column in df.columns:
        column_details.append({
            "name": column,
            "data_type": str(df[column].dtype),
            "missing_values": int(df[column].isnull().sum()),
            "unique_values": int(df[column].nunique())
        })

    duplicate_rows = int(df.duplicated().sum())

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    return {
        "rows": rows,
        "columns": columns,
        "column_details": column_details,
        "duplicate_rows": duplicate_rows,
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns
    }

if __name__ == "__main__":

    result = profile_dataset(
        "data/sample_sales.csv"
    )

    print(result)
