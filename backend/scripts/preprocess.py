import pandas as pd
import json
import os

# Definir el diccionario de mapeo
value_test_mapping = {
    'Negativo': 0,
    'Positivo': 1,
    'Positivo Fuerte': 1
}

# Limpia el CSV de datos y añade el número de mascotas por código postal
def clean_csv(data):
    column_mapping = {
        "Country": "country",
        "Pet sex": "sex",
        "Postal code": "post_code",
        "City": "city",
        "Geo Location": "location",
        "Value test": "result",
        "Pet age": "age",
        "Date": "date_done",
        "Name test": "desease"
    }
    
    # Renombrar las columnas
    data = data.rename(columns=column_mapping)

    # Eliminar columnas innecesarias
    data = data.drop(columns=["country", "location", "age"], errors="ignore")

    # Convertir la columna 'date_done' a formato de fecha
    data["date_done"] = pd.to_datetime(
        data["date_done"]
            .astype(str) 
            .str.replace('\ufeff', '', regex=True)  # Eliminar el BOM
            .str.replace('"', '', regex=True)       # Eliminar comillas extra
            .str.strip(),                           # Eliminar espacios en blanco
        errors='coerce'  # Si no se puede convertir, poner NaT
    )

    # Eliminar filas donde 'date_done' no pudo convertirse correctamente
    data = data.dropna(subset=["date_done"])

    # Filtrar solo valores válidos en 'result'
    valores_validos = list(value_test_mapping.keys())
    data = data[data["result"].isin(valores_validos)]

    # Mapear valores en 'result' (de 'Negativo' a 0 y 'Positivo' a 1)
    data["result"] = data["result"].map(value_test_mapping)

    # Asegurar que los valores en 'result' sean enteros
    data["result"] = data["result"].astype(int)

    # Asegurar que 'id_test' no tenga valores NaN y sea string
    if "id_test" in data.columns:
        data["id_test"] = data["id_test"].astype(str).fillna("")

    # Asegurar que 'post_code' y 'age' sean enteros (si hay valores NaN, poner 0)
    data["post_code"] = data["post_code"].fillna(0).astype(int)

    # Eliminar filas donde 'post_code', 'date_done' o 'desease' sean NaN
    required_columns = ["post_code", "date_done", "desease", "result"]
    data = data.dropna(subset=required_columns)

    # Agrupar los datos por código postal
    grouped_data = data.groupby('post_code').agg(
        casos_positivos=pd.NamedAgg(column='result', aggfunc='sum'),
        total_casos=pd.NamedAgg(column='result', aggfunc='count')
    ).reset_index()
    
    data = data.fillna({
        "post_code": 0,       # Si falta, poner 0
        "city": "Desconocido", # Si falta, poner un texto por defecto
        "sex": "Desconocido",  # Si falta, poner un texto por defecto
        "desease": "Desconocido", # Si falta, poner un texto por defecto
    })

    return data