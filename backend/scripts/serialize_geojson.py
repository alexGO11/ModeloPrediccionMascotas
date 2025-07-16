import json
import geopandas as gpd
from shapely.geometry import mapping

def serialize_geojson_rows(rows):
    # Cargar shapefile con geometrías por código postal
    shapefile_path = "data/codigos_postales.shp"
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.rename(columns={"COD_POSTAL": "post_code"})
    gdf["post_code"] = gdf["post_code"].astype(str).str.zfill(5)

    # Diccionario para buscar geometría por código postal
    geometry_lookup = {row["post_code"]: row["geometry"] for _, row in gdf.iterrows()}

    results = []

    for row in rows:
        try:
            result_data = row._mapping["result_data"]
            json_data = json.loads(result_data)

            features = []

            for item in json_data.get("features", []):
                props = item["properties"]
                post_code = props["post_code"]
                geometry = geometry_lookup.get(post_code)

                if geometry:
                    feature = {
                        "type": "Feature",
                        "geometry": mapping(geometry),
                        "properties": {
                            "post_code": props["post_code"],
                            "z_value": props["z_value"],
                            "z_value_normalized": props["z_value_normalized"],
                            "p_value": props["p_value"],
                            "n_positives": props["n_positives"]
                        }
                    }
                    features.append(feature)

            geojson = {
                "type": "FeatureCollection",
                "features": features
            }

            results.append({
                "date": row._mapping["end_date"].strftime("%Y-%m-%d"),
                "geojson": geojson
            })

        except Exception as e:
            print("Error parsing result_data:", e)
            continue

    return results
