import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import esda
from libpysal.weights import DistanceBand
import json

# Cargar el mapa de las provincias de España
url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/spain-provinces.geojson"
provinces = gpd.read_file(url)

df = pd.read_csv('C:/Users/pablo/Desktop/tfg/ModeloPrediccionMascotas/Prueba1/data.csv')
def extract_coordinates(geo_location):
    try:
        loc_json = json.loads(geo_location.replace('""', '"'))
        latitude = float(loc_json["latitude"])
        longitude = float(loc_json["longitude"])
        return latitude, longitude
    except (json.JSONDecodeError, KeyError, TypeError):
        return None, None

# Aplicar la función a cada fila para crear columnas de latitude y longitude
df['latitude'], df['longitude'] = zip(*df['geo_location'].apply(extract_coordinates))
df.drop(['geo_location', 'city', 'text_test'], inplace=True, axis='columns')

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

gdf.set_crs(epsg=4326, inplace=True)
provinces.to_crs(epsg=4326, inplace=True)

dist_band = DistanceBand.from_dataframe(gdf, threshold=200000, binary=True)

gi_star = esda.G_Local(df['test_value'], dist_band)
gdf['Gi'] = gi_star.Zs

# Asegurarse de que ambos GeoDataFrames tienen el mismo CRS (Sistema de Referencia de Coordenadas)
gdf.set_crs(epsg=4326, inplace=True)
provinces.to_crs(epsg=4326, inplace=True)

# Visualizar los resultados
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
provinces.boundary.plot(ax=ax, linewidth=1)
gdf.plot(column='Gi', cmap='coolwarm', ax=ax, legend=True, markersize=50)

plt.title('Puntos Calientes y Fríos según Getis-Ord por Provincias en España')
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.show()