import folium
from folium.plugins import HeatMap
import json

# Convertir datos a GeoJSON para poder hacer una visualización interactiva
geojson_data = {
    "type": "FeatureCollection",
    "features": []
}

for _, row in gdf.iterrows():
    feature = {
        "type": "Feature",
        "geometry": json.loads(row.geometry.to_json()),  # Convertir la geometría
        "properties": {
            "time": row["Fecha_test"].isoformat(),  # Convertir fecha en formato ISO
            "popup": f"Código Postal: {row['Postal code']}<br>Fecha: {row['Fecha_test'].date()}<br>Gi*: {row['z_value']:.2f}",
            "style": {
                "color": "red" if row["z_value"] > 1.96 else "blue" if row["z_value"] < -1.96 else "gray"
            }
        }
    }
    geojson_data["features"].append(feature)

# Crear mapa en Folium centrado en España
m = folium.Map(location=[40.4168, -3.7038], zoom_start=6)

# Agregar los datos con slider de tiempo
from folium.plugins import TimestampedGeoJson

TimestampedGeoJson(
    geojson_data,
    period="P1D",  # Intervalo de un día
    add_last_point=True,
    auto_play=True,
    loop=True,
    max_speed=1,
).add_to(m)

# Guardar el mapa interactivo
m.save("mapa_hotspots_temporal.html")
