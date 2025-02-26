import pandas as pd
from opencage.geocoder import OpenCageGeocode
import json
import os

# Definir el diccionario de mapeo
value_test_mapping = {
    'Negativo': 0,
    'Positivo': 1,
    'Positivo Fuerte': 1
}

# Limpia el csv de datos y añade el numero de mascotas por codigo postal
def clean_csv(file_name):
    #file_name = "data/raw/new_data.csv"
    
    data = pd.read_csv(file_name, dtype={'Postal code': str}, encoding='utf-8-sig')

    # Limpiar y convertir la columna 'Date'
    data['Date'] = pd.to_datetime(
    data['Date']
        .str.replace('\ufeff', '')  # Elimina el BOM
        .str.replace('"', '')       # Elimina las comillas extra
        .str.strip(),               # Elimina espacios en blanco
        format='%Y-%m-%d %H:%M:%S'
    )
    # Filtrar para conservar solo valores válidos en 'Value test'
    valores_validos = ['Positivo', 'Negativo', 'Positivo Fuerte']
    data = data[data["Value test"].isin(valores_validos)]

    # Mapear valores de 'Value test'
    data['Value test'] = data['Value test'].map(value_test_mapping)

    # Eliminar filas donde 'Postal code' o 'Geo Location' estén vacíos
    data_cleaned = data.dropna(subset=["Postal code"])
    
    grouped_data = data_cleaned.groupby('Postal code').agg(
        casos_positivos=pd.NamedAgg(column='Value test', aggfunc='sum'),
        total_casos=pd.NamedAgg(column='Value test', aggfunc='count')
    ).reset_index()
    
    #num_pets = pd.read_csv("data/raw/num_mascotas.csv", dtype={'Postal code': str}, encoding='utf-8-sig')
    # Si es necesario, estandariza el formato del código postal (ej. 5 dígitos)
    #num_pets["Postal code"] = num_pets["Postal code"].astype(str).str.zfill(5)

    # Realizar el merge entre los dos DataFrames usando la columna "Postal code" como clave
    """final_data = pd.merge(grouped_data, 
                        num_pets[['Postal code', 'Estimacion mascotas CP']], 
                        on='Postal code', 
                        how='left')

    # Opcional: renombrar la columna si lo deseas
    final_data.rename(columns={'Estimacion mascotas CP': 'Estimacion mascotas'}, inplace=True)"""
    
    data_cleaned.to_csv("data/processed/processed_data.csv", index=False)
    
    grouped_data.to_csv("data/processed/grouped_data.csv")

    return data_cleaned


    
clean_csv("data/raw/new_data.csv")
    