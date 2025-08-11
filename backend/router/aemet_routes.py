from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

import requests
import pandas as pd
import numpy as np
import json
import traceback

from config.db_connection import engine
from model.aemet import aemet

from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from scipy.interpolate import griddata
from shapely.geometry import Point, shape
from shapely.prepared import prep
import time

aemet_routes = APIRouter()
url = "/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones"

def parse_coords(coord):
    try:
        # Verificar si la coordenada tiene formato N/S o E/W
        direction = coord[-1]  # Último carácter (N/S/E/W)
        coord = coord[:-1]  # Eliminar la dirección para procesar el número

        # Extraer grados, minutos y segundos
        deg = int(coord[:2])  # Los primeros dos caracteres corresponden a los grados
        min_ = int(coord[2:4])  # Los siguientes dos caracteres corresponden a los minutos
        sec = int(coord[4:6]) if len(coord) >= 6 else 0  # Si hay segundos, extraemos

        # Convertir a decimal
        decimal = deg + min_ / 60 + sec / 3600

        # Asignar signo según la dirección
        if direction in ['S', 'W']:  # Si la dirección es Sur o Oeste, los valores son negativos
            decimal = -decimal

        return decimal
    except Exception as e:
        print(f"Error en la conversión de coordenadas: {e}")
        return None

@aemet_routes.post("/fill_db")
async def fill_db_aemet():
    try:
        print("Iniciando proceso para llenar la base de datos con datos de AEMET")

        # Obtener la última fecha añadida en la tabla aemet
        with engine.connect() as conn:
            last_date = conn.execute(select(func.max(aemet.c.date))).scalar()
            conn.commit()
            print("Última fecha añadida en aemet:", last_date)

        API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJwYWJsb2plYkB1Y20uZXMiLCJqdGkiOiI1N2UzNGU4MS00MjY2LTRjYTItOWYwMS1mZGQ4YjQ3OWY5NzYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc0NTE3ODY0NiwidXNlcklkIjoiNTdlMzRlODEtNDI2Ni00Y2EyLTlmMDEtZmRkOGI0NzlmOTc2Iiwicm9sZSI6IiJ9.Optbg-10mKcY_DqzoGLqF5cLR-X4oB7LqZsA2_21pJY"
        if not last_date:
            current_date = datetime(2022, 1, 1)
        else:
            current_date = datetime.strptime(last_date, "%Y-%m-%d")


        end_date = datetime.utcnow()
        total_insertados = 0

        df_coords = pd.read_csv("data/ListadoEstaciones.csv", sep=";", encoding="latin1")
        df_coords.rename(columns={
            "INDICATIVO": "indicativo",
            "LATITUD": "lat",
            "LONGITUD": "lon"
        }, inplace=True)

        print("Coordenadas originales:")
        print(df_coords[["lat", "lon"]].head())
        df_coords["lat"] = df_coords["lat"].apply(parse_coords)
        df_coords["lon"] = df_coords["lon"].apply(parse_coords)
        print("Coordenadas convertidas:")
        print(df_coords[["lat", "lon"]].head())
        while current_date <= end_date:
            time.sleep(1)
            
            next_date = current_date + timedelta(days=15)
            fechaIniStr = current_date.strftime("%Y-%m-%dT%H:%M:%SUTC")
            fechaFinStr = next_date.strftime("%Y-%m-%dT%H:%M:%SUTC")

            print(f"Solicitando metadatos: {fechaIniStr} - {fechaFinStr}")

            meta_url = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones"
            meta_response = safe_get(meta_url, params={"api_key": API_KEY})
            print("Respuesta de metadatos:", meta_response.json())
            if meta_response.status_code != 200:
                print(f"Error en la solicitud a AEMET: {meta_response.status_code}")
                break

            datos_url = meta_response.json().get("datos")
            if not datos_url:
                print("No se encontró la URL de datos en la respuesta.")
                break

            print("Descargando datos de:", datos_url)
            datos_response = requests.get(datos_url)
            if datos_response.status_code != 200:
                print(f"Error al descargar los datos: {datos_response.json()}")
                break

            registros = datos_response.json()
            print(f"Descargados {len(registros)} registros")
            clean_data = []

            for r in registros:
                try:
                    clean_data.append({
                        "indicativo": r["indicativo"],
                        "date": r["fecha"][:10],
                        "temp": float(r["tmed"].replace(",", ".")),
                        "location": r["provincia"]
                    })
                except (KeyError, ValueError):
                    continue

            df_aemet = pd.DataFrame(clean_data)
            if df_aemet.empty:
                print("No hay datos limpios para este intervalo")
                current_date = next_date
                continue

            df_agg = df_aemet.groupby(["indicativo", "location"]).agg(
                temp=("temp", "mean")
            ).reset_index()
            df_agg["date"] = current_date.strftime("%Y-%m-%d")

            df_merged = pd.merge(df_agg, df_coords[["indicativo", "lat", "lon"]], on="indicativo", how="inner")
            df_merged.dropna(subset=["lat", "lon"], inplace=True)

            with engine.connect() as conn:
                if not df_merged.empty:
                    conn.execute(aemet.insert(), df_merged.to_dict(orient="records"))
                    conn.commit()
                    total_insertados += len(df_merged)

            print(f"Intervalo {fechaIniStr} - {fechaFinStr} insertado con {len(df_merged)} registros")
            current_date = next_date
        
        

        return {"message": "Datos cargados correctamente", "total_insertados": total_insertados}

    except Exception as e:
        import traceback
        print("Traceback completo:")
        traceback.print_exc()
        return JSONResponse(
            content={"error": f"Error al procesar la solicitud: {str(e)}"},
            status_code=500,
    )
        
def safe_get(url, params=None, retries=5, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 429:
                print("Límite de peticiones alcanzado. Esperando...")
                time.sleep(60)
                continue
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"[Intento {attempt + 1}/{retries}] Error al solicitar {url}: {e}")
            time.sleep(delay)
    raise Exception(f"No se pudo obtener respuesta tras {retries} intentos.")

@aemet_routes.post("/get_data")
async def get_aemet_data(request: Request):
    raw_body = await request.body()
    results = []
   
    try:
        params = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        return JSONResponse(
            content={"error": "El cuerpo de la solicitud no es un JSON válido"},
            status_code=400,
        )

    try:
        print("Datos recibidos:", params)

        end_date = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
        current_date = datetime.strptime("2024-08-18", "%Y-%m-%d").date()
        interval = params["interval"]

        # Cargar shape de España (MultiPolygon)
        with open("data/shpESP.geojson", "r") as f:
            shape_geojson = json.load(f)
            shape_union = shape(shape_geojson)

        shape_prepared = prep(shape_union)  # Acelera los contains()
        minx, miny, maxx, maxy = shape_union.bounds  # Bounding box para filtro rápido

        print("Shape de España cargado y preparado")

        with engine.connect() as conn:

            stmt = stmt = select(func.max(aemet.c.temp))
            max_temp = conn.execute(stmt).scalar()
            print("Max temp:", max_temp)
            stmt = stmt = select(func.min(aemet.c.temp))
            min_temp = conn.execute(stmt).scalar()
            print("Min temp:", min_temp)

            while current_date >= end_date:
                next_date = current_date - timedelta(days=interval)
                print(f"Intervalo: {next_date} → {current_date}")
                
                stmt = (
                    select(
                        func.avg(aemet.c.temp).label("avg_temp"),
                        aemet.c.lon,
                        aemet.c.lat
                    )
                    .where(
                        and_(
                            aemet.c.date >= next_date.strftime("%Y-%m-%d"),
                            aemet.c.date <= current_date.strftime("%Y-%m-%d"),
                        )
                    )
                    .group_by(aemet.c.lon, aemet.c.lat)
                )

                result = conn.execute(stmt).mappings().fetchall()

                print(f"Registros encontrados: {len(result)}")

                if not result:
                    print(f"Sin datos en el intervalo {next_date} → {current_date}")
                    current_date = next_date
                    continue

                # Interpolación de temperaturas
                points = np.array([(row["lon"], row["lat"]) for row in result])
                values = np.array([row["avg_temp"] for row in result])

                lon_min, lon_max = -10, 5
                lat_min, lat_max = 35, 44
                grid_x, grid_y = np.mgrid[lon_min:lon_max:200j, lat_min:lat_max:200j]

                grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

                interpolated_features = []
                for i in range(grid_x.shape[0]):
                    for j in range(grid_x.shape[1]):
                        lon = float(grid_x[i, j])
                        lat = float(grid_y[i, j])
                        temp = float(grid_z[i, j])

                        if np.isnan(temp):
                            continue

                        if not (minx <= lon <= maxx and miny <= lat <= maxy):
                            continue 

                        punto = Point(lon, lat)
                        if shape_prepared.contains(punto):  
                            
                            temp_norm = (temp - min_temp) / (max_temp - min_temp) if max_temp != min_temp else 0

                            interpolated_features.append({
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [lon, lat]
                                },
                                "properties": {
                                    "temp": round(temp, 2),
                                    "temp_norm": round(temp_norm, 1)
                                }
                            })

                geojson = {
                    "type": "FeatureCollection",
                    "features": interpolated_features
                }

                results.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "geojson": geojson
                })

                current_date = next_date

        return JSONResponse(content=results)

    except Exception as e:
        print("Error interno:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))