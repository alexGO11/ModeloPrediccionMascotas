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

# Function to analyze coordinates in DMS format
def parse_coords(coord):
    try:
        # Verify if the coordinate has N/S or E/W format
        direction = coord[-1]  # Last character (n/s/and/w)
        coord = coord[:-1]  # Eliminate address to process the number

        # Extract degrees, minutes and seconds
        deg = int(coord[:2])  # The first two characters correspond to grades
        min_ = int(coord[2:4])  # The following two characters correspond to the minutes
        sec = int(coord[4:6]) if len(coord) >= 6 else 0  # If there are seconds, we extract

        # Turn to decimal
        decimal = deg + min_ / 60 + sec / 3600

        # Assign sign according to the address
        if direction in ['S', 'W']:  # If the address is south or west, the values ​​are negative
            decimal = -decimal

        return decimal
    except Exception as e:
        print(f"Error en la conversión de coordenadas: {e}")
        return None

# Endpoint to fill the database with AEMET data connecting directly with the official API
@aemet_routes.post("/fill_db")
async def fill_db_aemet():
    try:
        print("AEMET_ROUTES| Iniciando proceso para llenar la base de datos con datos de AEMET")

        # Obtain the last date added in Table Aemet
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

        print("AEMET_ROUTES| Coordenadas originales:")
        df_coords["lat"] = df_coords["lat"].apply(parse_coords)
        df_coords["lon"] = df_coords["lon"].apply(parse_coords)

        print("AEMET_ROUTES| Coordenadas convertidas")
        print(df_coords.head())
        while current_date <= end_date:
            time.sleep(1)
            
            next_date = current_date + timedelta(days=15)
            fechaIniStr = current_date.strftime("%Y-%m-%dT%H:%M:%SUTC")
            fechaFinStr = next_date.strftime("%Y-%m-%dT%H:%M:%SUTC")

            print(f"AEMET_ROUTES| Solicitando metadatos: {fechaIniStr} - {fechaFinStr}")

            meta_url = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones"
            meta_response = safe_get(meta_url, params={"api_key": API_KEY})
            print("AEMET_ROUTES| Respuesta de metadatos:", meta_response.json())
            if meta_response.status_code != 200:
                print(f"AEMET_ROUTES| Error en la solicitud a AEMET: {meta_response.status_code}")
                break

            datos_url = meta_response.json().get("datos")
            if not datos_url:
                print("AEMET_ROUTES| No se encontró la URL de datos en la respuesta.")
                break

            print("AEMET_ROUTES| Descargando datos de:", datos_url)
            datos_response = requests.get(datos_url)
            if datos_response.status_code != 200:
                print(f"AEMET_ROUTES| Error al descargar los datos: {datos_response.json()}")
                break

            registros = datos_response.json()
            print(f"AEMET_ROUTES| Descargados {len(registros)} registros")
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
                print("AEMET_ROUTES| No hay datos limpios para este intervalo")
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

            print(f"AEMET_ROUTES| Intervalo {fechaIniStr} - {fechaFinStr} insertado con {len(df_merged)} registros")
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

# Function for get requests safely
def safe_get(url, params=None, retries=5, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 429:
                print("AEMET_ROUTES| Límite de peticiones alcanzado. Esperando...")
                time.sleep(60)
                continue
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"[Intento {attempt + 1}/{retries}] Error al solicitar {url}: {e}")
            time.sleep(delay)
    raise Exception(f"No se pudo obtener respuesta tras {retries} intentos.")

# Endpoint to obtain AEMET data from the database
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
        offset = params["offset"]
        current_date = current_date + timedelta(days=offset)

        # Load Shape from Spain (Multipolygon)
        with open("data/shpESP.geojson", "r") as f:
            shape_geojson = json.load(f)
            shape_union = shape(shape_geojson)

        shape_prepared = prep(shape_union)  # Calves the counts()
        minx, miny, maxx, maxy = shape_union.bounds  # Bounding Box for Fast Filter

        print("AEMET_ROUTES| Shape de España cargado y preparado")

        with engine.connect() as conn:

            stmt = stmt = select(func.max(aemet.c.temp))
            max_temp = conn.execute(stmt).scalar()
            print("AEMET_ROUTES| Max temp:", max_temp)

            stmt = stmt = select(func.min(aemet.c.temp))
            min_temp = conn.execute(stmt).scalar()
            print("AEMET_ROUTES| Min temp:", min_temp)

            while current_date >= end_date:
                next_date = current_date - timedelta(days=interval)
                print(f"AEMET_ROUTES| Intervalo: {next_date} → {current_date}")

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

                print(f"AEMET_ROUTES| Registros encontrados: {len(result)}")

                if not result:
                    print(f"AEMET_ROUTES| Sin datos en el intervalo {next_date} → {current_date}")
                    current_date = next_date
                    continue

                # Temperature interpolation
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