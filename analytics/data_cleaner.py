from __future__ import annotations

import pandas as pd


def _read_dataset(file_path: str) -> pd.DataFrame:
    if str(file_path).lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)
    return pd.read_csv(file_path)


def clean_dataset(file_path: str) -> dict:

    df = _read_dataset(file_path)

    original_rows = len(df)

    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    duplicate_rows = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)

    df.columns = [
        str(column).strip().lower().replace(" ", "_").replace("-", "_")
        for column in df.columns
    ]

    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("object")
            .where(df[column].notna(), "Unknown")
            .astype(str)
            .str.strip()
            .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
        )

    for column in df.columns:
        if "date" in column or "time" in column:
            converted = pd.to_datetime(df[column], errors="coerce")
            if converted.notna().sum() > 0:
                df[column] = converted

    numerical_columns = df.select_dtypes(include="number").columns

    for column in numerical_columns:
        df[column] = df[column].fillna(df[column].median())

    final_rows = len(df)

    if final_rows == 0:
        raise ValueError(
            "No usable rows remained after cleaning. "
            "Please check the file contents and try again."
        )

    return {
        "original_rows": original_rows,
        "final_rows": final_rows,
        "duplicates_removed": duplicate_rows,
        "cleaned_data": df,
    }

if __name__ == "__main__":

    result = clean_dataset("data/sample_sales.csv")

    print("Original rows:", result["original_rows"])
    print("Final rows:", result["final_rows"])
    print("Duplicates removed:", result["duplicates_removed"])
    print("\nData types:")
    print(result["cleaned_data"].dtypes)
