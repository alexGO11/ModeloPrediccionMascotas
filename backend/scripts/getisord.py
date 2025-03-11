import geopandas as gpd
import numpy as np
from libpysal.weights import Queen
from esda.getisord import G_Local
from shapely.geometry import mapping


def aply_getisord(df, census):
    # Cargar el shapefile con los códigos postales
    shapefile_path = "data/codigos_postales.shp"
    gdf = gpd.read_file(shapefile_path)

    # Limpiar columnas no necesarias
    gdf = gdf.rename(columns={"COD_POSTAL": "post_code"})
    gdf["post_code"] = gdf["post_code"].astype(str)

    # Agrupar los datos de tests positivos
    resultado = df.groupby("post_code").agg(
        Tests_Positivos=("result", "sum"),
        Total_Tests=("result", "count")
    ).reset_index()

    resultado["post_code"] = resultado["post_code"].astype(str)

    # Unir los datos espaciales con los tests
    gdf = gdf.merge(resultado, on="post_code", how="inner")
    
    gdf = gdf.merge(census, on="post_code", how="inner")
    
    # Verificar si `gdf` tiene datos después del merge
    if gdf.empty:
        raise ValueError("Error: No hay datos después del merge entre `gdf` y `resultado`.")

    # Calcular la tasa de positividad
    gdf["tasa_positividad"] = gdf["Tests_Positivos"] / gdf["census"]

    # Construir la matriz de pesos espaciales
    try:
        w = Queen.from_dataframe(gdf)
    except StopIteration:
        raise ValueError("Error: No hay suficientes polígonos válidos para construir la matriz de pesos espaciales.")

    # Aplicar el estadístico de Getis-Ord G*
    g = G_Local(gdf["tasa_positividad"], w)

    # Guardar resultados en el DataFrame
    gdf["z_value"] = g.Zs
    gdf["p_value"] = g.p_sim

    # Reemplazar NaN en valores de z_score
    gdf["z_value"] = gdf["z_value"].fillna(0)

    # Asignar etiquetas de hotspot/coldspot
    gdf['hotspot'] = np.where((gdf['z_value'] > 0) & (gdf['p_value'] < 0.05), 'Hotspot',
                               np.where((gdf['z_value'] < 0) & (gdf['p_value'] < 0.05), 'Coldspot', 'Not Significant'))

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    print(gdf.columns)
    for _, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "geometry": mapping(row["geometry"]),  # Convertir a GeoJSON
            "properties": {
                "post_code": row["post_code"],
                "z_value": row["z_value"],
            }
        }
        geojson["features"].append(feature)

    return geojson

