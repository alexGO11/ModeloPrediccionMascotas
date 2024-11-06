import pandas as pd
import json
from geopy.geocoders import Nominatim
import time  # Para agregar retraso entre solicitudes a la API de geocodificación

# Ruta al archivo de Excel
file_path = 'C:/Users/pablo/Documents/tfg-prueba/enfermedades.xlsx'  
geolocator = Nominatim(user_agent="mi_app_geocodificacion")

# Función para obtener la ciudad a partir de coordenadas
def obtener_ciudad(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True)
        if location and 'city' in location.raw['address']:
            return location.raw['address']['city']
        elif location and 'town' in location.raw['address']:
            return location.raw['address']['town']
        elif location and 'village' in location.raw['address']:
            return location.raw['address']['village']
    except Exception as e:
        print(f"Error obteniendo la ciudad para coordenadas ({lat}, {lon}): {e}")
    return None

# Cargar el archivo de Excel
try:
    excel_data = pd.ExcelFile(file_path)
    print("Hojas en el archivo:", excel_data.sheet_names)  # Verifica las hojas en el archivo
    
    # Cargar la hoja específica en un DataFrame
    df = excel_data.parse('diro_positive_spain_port')

    # Función para extraer coordenadas de 'geo_location'
    def extract_coordinates(location):
        try:
            loc_json = json.loads(location)  # Parsear JSON directamente
            return float(loc_json["latitude"]), float(loc_json["longitude"])
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error en la fila con geo_location = {location}: {e}")
            return None, None

    # Verificar que 'geo_location' existe y extraer latitud y longitud
    if 'geo_location' in df.columns:
        df['latitude'], df['longitude'] = zip(*df['geo_location'].apply(extract_coordinates))

        # Filtrar filas con coordenadas válidas
        df_clean = df.dropna(subset=['latitude', 'longitude']).copy()

        # Aplicar la función obtener_ciudad para rellenar la columna 'city'
        df_clean['city'] = df_clean.apply(lambda row: obtener_ciudad(row['latitude'], row['longitude']), axis=1)

        # Guardar en CSV solo las columnas especificadas
        df_clean.to_csv(
            'C:/TFG/prepared_enfermedades.csv', 
            index=False, 
            encoding='utf-8', 
            columns=['id', 'geo_location', 'city', 'postal_code', 'text_test']
        )

        # Mostrar las primeras filas para verificar el resultado
        print(df_clean[['id', 'latitude', 'longitude', 'city', 'text_test']].head())
    else:
        print("La columna 'geo_location' no se encuentra en el DataFrame.")
        
except FileNotFoundError:
    print(f"El archivo no se encuentra en la ruta: {file_path}")
except Exception as e:
    print(f"Ocurrió un error: {e}")
