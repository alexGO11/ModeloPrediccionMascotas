import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import matplotlib.pyplot as plt
import json

# Cargar el archivo GeoJSON de provincias de España
url_geojson = 'https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.geojson'
gdf = gpd.read_file(url_geojson)

# Cargar el archivo CSV de datos y extraer las coordenadas
bl_df = pd.read_csv('C:/Users/pablo/Desktop/tfg/ModeloPrediccionMascotas/Prueba1/prepared_enfermedades.csv')

# Función para extraer latitude y longitude de la columna geo_location
def extract_coordinates(geo_location):
    try:
        loc_json = json.loads(geo_location.replace('""', '"'))
        latitude = float(loc_json["latitude"])
        longitude = float(loc_json["longitude"])
        return latitude, longitude
    except (json.JSONDecodeError, KeyError, TypeError):
        return None, None

# Aplicar la función a cada fila para crear columnas de latitude y longitude
bl_df['latitude'], bl_df['longitude'] = zip(*bl_df['geo_location'].apply(extract_coordinates))

# Crear la geometría de puntos usando las coordenadas extraídas
geometry = [Point(xy) for xy in zip(bl_df.longitude, bl_df.latitude)]
bl_gdf = GeoDataFrame(bl_df, crs="EPSG:4326", geometry=geometry)

# Asegurarse de que ambos GeoDataFrames están en el mismo CRS
gdf = gdf.to_crs(bl_gdf.crs)

# Graficar el mapa de provincias con los puntos de datos
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, color='lightgrey', edgecolor='black')  # Provincias
bl_gdf.plot(ax=ax, color='red', markersize=5, alpha=0.7)  # Puntos de datos
plt.title('Mapa de Provincias de España con Ubicaciones de Datos')
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.show()
