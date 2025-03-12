import geopandas as gpd
import numpy as np
from libpysal.weights import Queen
from esda.getisord import G_Local
from shapely.geometry import mapping


def aply_getisord(df, census):
    print("Tests encontrados en el intervalo de tiempo: ", len(df))
    print(df.head())
    
    shapefile_path = "data/codigos_postales.shp"
    gdf = gpd.read_file(shapefile_path)

    # Renombrar columnas
    gdf = gdf.rename(columns={"COD_POSTAL": "post_code"})
    
    print("Shapes cargados: ", len(gdf))
    print(gdf.head())

    # Agrupar los datos de tests positivos
    resultado = df.groupby("post_code").agg(
        Tests_Positivos=("result", "sum"),
        Total_Tests=("result", "count")
    ).reset_index()

    # Unir los datos espaciales con los tests
    gdf = gdf.merge(resultado, on="post_code", how="inner")
    
    print("Datos mergeados: ", len(gdf))
    if gdf.empty:
        print("No hay datos después del merge con resultados, devolviendo GeoJSON vacío.")
        return {"type": "FeatureCollection", "features": []}

    gdf = gdf.merge(census, on="post_code", how="left")
    
    # Si sigue sin datos después del merge con census, devolver vacío
    if gdf.empty:
        print("No hay datos después del merge con census, devolviendo GeoJSON vacío.")
        return {"type": "FeatureCollection", "features": []}

    # Rellenar posibles valores NaN en census
    gdf["census"] = gdf["census"].fillna(1)

    # Calcular la tasa de positividad
    gdf["tasa_positividad"] = gdf["Tests_Positivos"] / gdf["census"]
    
    # Filtrar geometrías válidas
    gdf = gdf[gdf.geometry.is_valid]  
    gdf = gdf[gdf.geometry.area > 0]  
    gdf = gdf[gdf.geometry.is_empty == False]  

    # Verificar si quedan suficientes datos
    if len(gdf) < 4:
        print("Demasiados pocos datos para análisis espacial, devolviendo GeoJSON vacío.")
        return {"type": "FeatureCollection", "features": []}

    # Construir la matriz de pesos espaciales
    try:
        w = Queen.from_dataframe(gdf)
    except StopIteration:
        print("No hay suficientes polígonos válidos para construir la matriz de pesos espaciales.")
        return {"type": "FeatureCollection", "features": []}

    print("Tasas de positividad:")
    print(gdf["tasa_positividad"].shape)

    # Aplicar el estadístico de Getis-Ord G*
    g = G_Local(gdf["tasa_positividad"], w)

    # Guardar resultados en el DataFrame
    gdf["z_value"] = g.Zs
    gdf["p_value"] = g.p_sim

    # Reemplazar NaN en valores de z_score
    gdf["z_value"] = gdf["z_value"].fillna(0)
    
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for _, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "geometry": mapping(row["geometry"]),  
            "properties": {
                "post_code": row["post_code"],
                "z_value": row["z_value"],
            }
        }
        geojson["features"].append(feature)

    return geojson
