import pandas as pd

df = pd.read_csv("data/raw/new_data.csv")

count_nan = df["Postal code"].isna().sum()
print(f"Filas con NaN: {count_nan}")