# Python file in charge to preprocess the data

import pandas as pd
from opencage.geocoder import OpenCageGeocode
from tqdm import tqdm
import json

value_test_mapping = {
    'Dudoso': 0,
    'Error': 0,
    'Invalido': 0,
    'Inválido': 0,
    'Negativo': 0,
    'Positivo': 1,
    'Positivo Fuerte': 1
}
# Inicializa tqdm en Pandas
tqdm.pandas()

# Inicializa el geocoder con la clave de API
OCG = OpenCageGeocode('9a24a21e41604ae381a631608c343163')

# Función para obtener el código postal a partir de Geo Location
def get_postal_code(geo_location):
    try:
        # Convertir la cadena JSON en un diccionario
        location = json.loads(geo_location)
        lat = location['latitude']
        lng = location['longitude']
        # Realizar la búsqueda inversa
        results = OCG.reverse_geocode(lat, lng)
        if results and 'postcode' in results[0]['components']:
            return results[0]['components']['postcode']
    except Exception as e:
        print(f"Error procesando {geo_location}: {e}")
    return ""

# Leer el archivo CSV
file_path = "data/raw/new_data.csv" 
data = pd.read_csv(file_path, dtype={'Postal code': str})

# Limpiar codigos postales no validos
data['Postal code'] = data.progress_apply(
    lambda row: get_postal_code(row['Geo Location']) if pd.isna(row['Postal code']) and pd.notna(row['Geo Location']) else row['Postal code'],
    axis=1
)
data = data[data["Postal code"].notna() & (data["Postal code"].str.strip() != "")]
data["Postal code"] = data["Postal code"].astype(str).str.zfill(5)

# Mapear y convertir valores de 'Value test'
data['Value test'] = data['Value test'].map(value_test_mapping)
data['Value test'] = data['Value test'].fillna(0).astype(int)

# Eliminar filas donde ambas variables 'Postal code' y 'Geo Location' estén vacías
data_cleaned = data[~(data["Postal code"].isnull() & data["Geo Location"].isnull())]

# Modificar 'City' si el código postal es 6430
data_cleaned['City'] = data_cleaned.progress_apply(
    lambda row: 'Zalamea De La Serena' if row['Postal code'] == '06430' else row['City'], axis=1
)

# Eliminar los caracteres innecesarios
data_cleaned['Date'] = data_cleaned['Date'].str.replace('﻿"', '', regex=False)  # Eliminar el carácter especial ﻿
data_cleaned['Date'] = data_cleaned['Date'].str.replace('"', '', regex=False)  # Eliminar las comillas dobles

# Convertir la columna 'Date' a un formato de fecha y hora
data_cleaned['Date'] = pd.to_datetime(data_cleaned['Date'].progress_apply(lambda x: x.strip() if isinstance(x, str) else x), format='%Y-%m-%d %H:%M:%S')

# Limpiar los string que puede haber en la edad
data_cleaned["Pet age"] = pd.to_numeric(data_cleaned["Pet age"].str.extract(r"(\d+)")[0], errors='coerce')
data_cleaned["Pet age"] = data_cleaned["Pet age"].astype('Int64')

# Agrupar por 'Postal code' y sumar los valores de 'Value test'
grouped_data = data_cleaned.groupby("Postal code", as_index=False)["Value test"].sum()

# Guardar los archivos agrupados y procesados
for output_path, df in tqdm([
    ("data/processed/grouped_data.csv", grouped_data),
    ("data/processed/process_data.csv", data_cleaned)
], desc="Guardando archivos"):
    df.to_csv(output_path, index=False)