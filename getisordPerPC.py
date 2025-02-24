# imports
import pandas as pd

import geopandas as gpd
from libpysal.weights import DistanceBand

from esda import G_Local
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

df = pd.read_csv("data/new_data.csv", dtype={'Postal code': str})

# fitler to get two columns
df = df[['Value test', 'Postal code']]

# change postal codes with 4 digits to 5 addin a 0 in the left
df['Postal code'] = df['Postal code'].str.zfill(5)

# load postal codes shapefile to get polygon
gdf_postal_info = gpd.read_file("data/codigos_postales/codigos_postales.shp")
gdf_postal_info = gdf_postal_info.rename(columns={'COD_POSTAL': 'Postal code'})
gdf_postal_info = gdf_postal_info[['Postal code', 'geometry']]

# Contar el número total de resultados y positivos por código postal
positive_rate_df = (
    df.assign(is_positive = lambda x: x['Value test'] > 0)  # Crear una columna booleana
    .groupby('Postal code')  # Agrupar por código postal
    .agg(total_cases = ('Value test', 'size'),  # Total de casos
         positive_cases = ('is_positive', 'sum'))  # Total de casos positivos
    .assign(positivity_rate = lambda x: x['positive_cases'] / x['total_cases'] * 100)  # Calcular porcentaje
)


# merge both dataframes to work with df
df_merged = pd.merge(positive_rate_df, gdf_postal_info, on='Postal code', how='left')

# Cargar los datos en un GeoDataFrame
gdf = gpd.GeoDataFrame(df_merged, geometry='geometry', crs="EPSG:4326")
gdf = gdf.to_crs("EPSG:25830")

gdf = gdf[gdf.is_valid]

# Crear la matriz de ponderación basada en una distancia de 5 km (ajustable)
w = DistanceBand.from_dataframe(gdf, threshold=5000, binary=True)
w.transform = 'r' # normalize

# Calculate Getis-Ord Gi*
g = G_Local(gdf['positivity_rate'], w)

# Obtain z-values y p-values
z_values = g.Zs  # Array with z-value
p_values = g.p_sim  # Array with p-value

# Agregar los resultados al GeoDataFrame
gdf['z_value'] = z_values
gdf['p_value'] = p_values

# Filtrar puntos calientes y fríos significativos
gdf['hotspot'] = np.where((gdf['z_value'] > 0) & (gdf['p_value'] < 0.05), 'Hotspot',
                          np.where((gdf['z_value'] < 0) & (gdf['p_value'] < 0.05), 'Coldspot', 'Not Significant'))

# Crear un mapeo de colores personalizado
colors = ['red', 'blue', 'gray']  # Hotspot: rojo, Coldspot: azul, Not Significant: gris
cmap = ListedColormap(colors)

# Asignar un índice a cada categoría
hotspot_categories = {'Hotspot': 0, 'Coldspot': 1, 'Not Significant': 2}
gdf['hotspot_code'] = gdf['hotspot'].map(hotspot_categories)

# Visualización
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(column='hotspot_code', cmap=cmap, legend=False, ax=ax)

# Añadir una leyenda personalizada
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Hotspot'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Coldspot'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Not Significant')
]
ax.legend(handles=legend_elements, loc='upper right')

# Título del gráfico
plt.title("Getis-Ord Gi* Hotspots and Coldspots")
plt.show()