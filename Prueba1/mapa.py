import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import matplotlib.pyplot as plt
import json
import esda
import numpy as np
from libpysal.weights import KNN

# Cargar el archivo GeoJSON de provincias de España
url_geojson = 'https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.geojson'
gdf = gpd.read_file(url_geojson)

# Cargar el archivo CSV de datos y extraer las coordenadas
bl_df = pd.read_csv('C:/Users/pablo/Desktop/tfg/ModeloPrediccionMascotas/Prueba1/data.csv')

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
bl_df.drop(['geo_location', 'city', 'text_test'], inplace=True, axis='columns')

print(bl_df)

# Crear la geometría de puntos usando las coordenadas extraídas
geometry = [Point(xy) for xy in zip(bl_df.longitude, bl_df.latitude)]
bl_gdf = GeoDataFrame(bl_df, crs="EPSG:4326", geometry=geometry)


# Asegurarse de que ambos GeoDataFrames están en el mismo CRS
gdf = gdf.to_crs(bl_gdf.crs)

# Hacer una unión espacial para asignar cada punto a una provincia
sj_gdf = gpd.sjoin(gdf, bl_gdf, how='inner', predicate='intersects')

# Calcular la media de la variable numérica para cada provincia
province_means = sj_gdf.groupby('name')['test_value'].mean()
gdf = gdf.join(province_means, on='name')
gdf['test_value'] = gdf['test_value'].fillna(0)

# Convertir a un CRS proyectado para el cálculo de centroides
gdf = gdf.to_crs(epsg=4326)
coords = np.array(list(gdf.geometry.centroid.apply(lambda point: (point.x, point.y))))

# Crear la matriz de pesos espaciales KNN
weights = KNN.from_array(coords, k=7)

# Calcular el estadístico de Getis-Ord G*
gi_star = esda.G_Local(gdf['test_value'], weights)

# Añadir los resultados al GeoDataFrame
gdf['Gi_star'] = gi_star.Zs  # Los valores Z indican la intensidad de los hotspots/coldspots

print(gdf[['name', 'Gi_star']])

# Convertir de vuelta al CRS geográfico para la visualización
gdf = gdf.to_crs(epsg=4326)

# Colorear el mapa en función de los valores de Getis-Ord
fig, ax = plt.subplots(figsize=(12, 10))
gdf.plot(column='Gi_star', cmap='coolwarm', scheme='quantiles', k=5, legend=True, ax=ax)
plt.title('Mapa de Provincias con Hotspots y Coldspots')
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.show()
