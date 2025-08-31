import pandas as pd

# Function to clean pet data
def prepare_test_data(data):
    column_mapping = {
        "Country": "country",
        "Pet sex": "sex",
        "Postal code": "post_code",
        "City": "city",
        "Geo Location": "location",
        "Value test": "result",
        "Pet age": "age",
        "Date": "date_done",
        "Name test": "disease"
    }
    
    # Define the mapping dictionary
    value_test_mapping = {
        'Negativo': 0,
        'Positivo': 1,
        'Positivo Fuerte': 1
    }

    # Rename the columns
    data = data.rename(columns=column_mapping)

    # Eliminate unnecessary columns
    data = data.drop(columns=["location", "country"], errors="ignore")

    # Convert the 'date_done column to date format
    data["date_done"] = pd.to_datetime(
        data["date_done"]
            .astype(str) 
            .str.replace('\ufeff', '', regex=True)  # Eliminate bom

            .str.replace('"', '', regex=True)       # Remove extra quotes

            .str.strip(),                           # Eliminate blank spaces

        errors='coerce'  # If it can't be converted, put nat

    )

    # Eliminate rows where 'date_done' could not become properly
    data = data.dropna(subset=["date_done"])

    # Filter only valid values ​​in 'results'
    valores_validos = list(value_test_mapping.keys())
    data = data[data["result"].isin(valores_validos)]

    # Map values ​​in 'results' (from 'negative' to 0 and 'positive' to 1)
    data["result"] = data["result"].map(value_test_mapping)

    # Ensure that the values ​​in 'results' are whole
    data["result"] = data["result"].astype(int)

    # Ensure that 'id_test' does not have nan values ​​and is string
    if "id_test" in data.columns:
        data["id_test"] = data["id_test"].astype(str).fillna("")
        
    # Ensure that 'post_code' is 5 digit string
    data["post_code"] = data["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

    # Ensure that 'post_code' and 'age' are whole (if there are nan values, put 0)
    data["post_code"] = data["post_code"].fillna(0).astype(int)

    # Clean the 'AGE' column to eliminate the pattern 'year/s' and handle missing or invalid values
    data["age"] = data["age"].str.extract(r"(\d+)")
    data["age"] = pd.to_numeric(data["age"], errors="coerce")
    data["age"] = data["age"].fillna(0).astype(int)

    # Replace null values ​​in the 'city' column with 'unknown'
    data["city"] = data["city"].fillna("desconocido")

    # Replace null values ​​in the 'sex' column with 'unknown'
    data["sex"] = data["sex"].fillna("desconocido")


    # Eliminate rows where 'post_code', 'date_done' or 'disassembly' are nan
    required_columns = ["post_code", "date_done", "disease", "result"]
    data = data.dropna(subset=required_columns)

    print("Datos preparados:")
    print(data.head())

    return data

# Function to prepare census data by postal code
def prepare_post_code_data(data):

    # Filter and rename columns
    column_mapping = {
        "COD_POSTAL": "post_code",
        "Censo_mascota_CP": "census"
    }

    data = data[list(column_mapping.keys())].rename(columns=column_mapping)

    # Verify NAN values ​​before conversion
    print("Valores NaN en 'census':", data["census"].isna().sum())

    # Fill Nan with 0.0 and make sure that Census is float
    data["census"] = data["census"].fillna(0.0).astype(float)

    # Filter for census that are greater than or equal to 1
    data["census"] = data["census"].replace(0, 1)

    # Ensure that 'post_code' is 5 digit string
    data["post_code"] = data["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

    return data