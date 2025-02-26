# Python file in charge to preprocess the data

import pandas as pd
from opencage.geocoder import OpenCageGeocode
import json

value_test_mapping = {
    'Dudoso': -2,
    'Error': -1,
    'Invalido': -1,
    'Inválido': -1,
    'Negativo': 0,
    'Positivo': 1,
    'Positivo Fuerte': 2
}

# Leer el archivo CSV
file_path = "data/new_data.csv" 
data = pd.read_csv(file_path, dtype={'Postal code': str})
data["Postal code"] = data["Postal code"].astype(str).str.zfill(5)

# Mapear y convertir valores de 'Value test'
data['Value test'] = data['Value test'].map(value_test_mapping)
data['Value test'] = data['Value test'].fillna(0).astype(int)

# Eliminar filas donde ambas variables 'Postal code' y 'Geo Location' estén vacías
data_cleaned = data[~(data["Postal code"].isnull() & data["Geo Location"].isnull())]

# Modificar 'City' si el código postal es 6430
data_cleaned['City'] = data_cleaned.apply(
    lambda row: 'Zalamea De La Serena' if row['Postal code'] == '06430' else row['City'], axis=1
)

# Eliminar los caracteres innecesarios
data_cleaned['Date'] = data_cleaned['Date'].str.replace('﻿"', '', regex=False)  # Eliminar el carácter especial ﻿
data_cleaned['Date'] = data_cleaned['Date'].str.replace('"', '', regex=False)  # Eliminar las comillas dobles

# Convertir la columna 'Date' a un formato de fecha y hora
data_cleaned['Date'] = pd.to_datetime(data_cleaned['Date'], format='%Y-%m-%d %H:%M:%S')

# Agrupar por 'Postal code' y sumar los valores de 'Value test'
grouped_data = data_cleaned.groupby("Postal code", as_index=False)["Value test"].sum()

# Guardar el archivo agrupado con las sumas
grouped_output_path = "data/processed/grouped_data.csv"
grouped_data.to_csv(grouped_output_path, index=False)

# Guardar el archivo completo procesado
processed_output_path = "data/processed/process_data.csv"
data_cleaned.to_csv(processed_output_path, index=False)