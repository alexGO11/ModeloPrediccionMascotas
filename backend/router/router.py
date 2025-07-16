from fastapi import APIRouter, Response, Request, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import requests
from starlette.status import HTTP_201_CREATED
from schema.test_schema import TestSchema
from schema.pc_schema import PostalCodeSchema
from schema.precalculated_schema import PrecalculatedSchema
from model.precalculated import precalculated
import pandas as pd
import numpy as np
import json
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from config.db import engine
from model.tests import tests
from typing import List
from scripts.preprocess import clean_csv
from scripts.getisord import aply_getisord
from model.postal_code import pc
from model.getisord_t import getis_ord
from model.aemet import aemet
from schema.aemet_schema import AemetSchema
import traceback
import numpy as np
from scipy.interpolate import griddata
from shapely.geometry import mapping, Point
from shapely.geometry import shape
from shapely.prepared import prep
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from scripts.serialize_geojson import serialize_geojson_rows
import time



test = APIRouter()
url = "/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones"
scheduler = AsyncIOScheduler()

intervals = [15, 30, 60, 90, 120]
diseases = ["Leishmania", "Giardia"]

@test.get("/")
def root():
    return {"message": "hi im fastAPI with a router"}

        
# Recibe un intervalo de timpo introducido por el usuario y devuelve los datos de todos los tests realizados separados por intervalos de tiempo
@test.post("/api/test/filtered")
async def get_tests_filtered(request: Request):
    raw_body = await request.body()

    try:
        params = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "El cuerpo no es JSON válido"}, status_code=400)

    print("Datos recibidos:", params)

    if "start_date" not in params:
        return JSONResponse(content={"error": "Falta start_date"}, status_code=400)

    # Inicializa variables
    start_date = datetime.utcnow()
    end_date = datetime.strptime("2022-01-01", "%Y-%m-%d")
    interval = params["interval"]
    disease = params["disease"]

    # Si el intervalo coincide con los precalculados, devolverlos
    if interval in [15, 30, 60, 90, 120]:
        with engine.connect() as conn:
            query = select(precalculated).where(
                and_(
                    precalculated.c.days_interval == f"{interval}D",
                    precalculated.c.disease == disease
                )
            ).order_by(precalculated.c.end_date.desc())

            result = conn.execute(query)
            rows = result.fetchall()

            print("Datos precalculados encontrados:", len(rows))
            
            geojson = serialize_geojson_rows(rows)

            

            return JSONResponse(content=geojson)

    # Si no hay datos precalculados, calcularlos manualmente
    results = []

    with engine.connect() as conn:
        print("Conectado a la base de datos")
        current_date = start_date

        census_db = conn.execute(select(pc))
        census = pd.DataFrame(census_db.fetchall(), columns=census_db.keys())

        # Recorre todas las fechas con saltos temporales = al intervalo
        while current_date >= end_date:
            next_date = current_date - timedelta(days=interval)

            query = select(tests).where(
                and_(
                    tests.c.date_done <= current_date,
                    tests.c.date_done > next_date,
                    tests.c.desease == disease
                )
            )

            result = conn.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

            # Si hay datos, aplicar el algoritmo de Getis-Ord y los resultados se añaden a la lista
            if not df.empty:
                df_resultado = aply_getisord(df, census)


                results.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "geojson": df_resultado
                })

            current_date = next_date

    return JSONResponse(content=results)



# Genera datos precalculados para todos los intervalos de tiempo y enfermedades
@test.post("/api/test/precalculated", status_code=HTTP_201_CREATED)
async def create_precalculated_data():
    try:
        # Limpiar la tabla antes de insertar nuevos datos y obtiener el censo
        with engine.connect() as conn:
            conn.execute(precalculated.delete())  
            query = select(pc)
            census_db = conn.execute(query)
            census = pd.DataFrame(census_db.fetchall(), columns=census_db.keys())
            conn.commit()

        start_date = datetime.utcnow()
        end_date = datetime.strptime("2022-01-01", "%Y-%m-%d")
        print("End date:", end_date)

        current_date = start_date

        # Para cada intervalo de tiempo y enfermedad, se obtiene los datos y aplicamos getis-ord para luego almacenar los resultados en la base de datos
        for interval in intervals:
            current_date = start_date
            while current_date >= end_date:
                for disease in diseases:

                        
                        with engine.connect() as conn:
                            print("Conectado a la base de datos")
                            

                            print("Current date:", current_date)
                            next_date = current_date - timedelta(days=interval)
                            print("Start date:", start_date)
                            print("Next date:", next_date)
                            print("Interval:", interval)

                            # Consulta filtrando por el intervalo de tiempo actual
                            query = select(tests).where(
                                    and_(
                                        tests.c.date_done <= current_date,
                                        tests.c.date_done > next_date,
                                        tests.c.desease == disease
                                    )
                                )
                            print("Query:", query)
                            result = conn.execute(query)
                            df = pd.DataFrame(result.fetchall(), columns=result.keys())
                            df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)
                                
                            try:
                                df_resultado = aply_getisord(df, census)
                                # Si el resultado es vacío se rellena con JSON vacio
                                if not df_resultado or not df_resultado.get("features"):  # Vacío o sin features
                                    print("GeoJSON vacío, insertando estructura mínima")
                                    df_resultado = {"type": "FeatureCollection", "features": []}

                                # Eliminar geometria para facilitar el almacenado en la base de datos
                                for feature in df_resultado["features"]:
                                    feature.pop("geometry", None)

                                conn.execute(
                                    precalculated.insert().values(
                                        disease=disease,
                                        days_interval=f"{interval}D",
                                        end_date=current_date,
                                        result_data=json.dumps(df_resultado)
                                    )
                                )
                            except Exception as e:
                                print("Fallo al insertar:", e)
                            conn.commit()
                            
                            current_date = next_date
                
        return {"message": "Datos precalculados insertados correctamente"}
    except Exception as e:
        print("Error al insertar datos precalculados:", e)
        return JSONResponse(
            content={"error": f"Error al procesar la solicitud: {str(e)}"},
            status_code=500,
        )


#añade tests a la base de datos subiendo un csv
@test.post("/api/test/upload_csv", status_code=201)
async def upload_csv(file: UploadFile = File(...)):
    df = None
    try:
        file.file.seek(0)

        df = pd.read_csv(file.file)

        if df.empty:
            raise ValueError("El archivo CSV está vacío")

        print(df.head())
        df = clean_csv(df)
        print(df.head())
        
        
        df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

        data_to_insert = df.to_dict(orient="records")

        with engine.connect() as conn:
            conn.execute(tests.insert().values(data_to_insert))
            conn.commit()
            
        # Generamos nuevos datos precalculados
        create_precalculated_data()

        return {"message": "Datos insertados correctamente", "total": len(data_to_insert)}

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío o no tiene contenido válido")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el CSV, verifica el formato del archivo")
    except Exception as e:
        error_detail = f"Error procesando el archivo CSV: {str(e)}"
        if df is not None:
            error_detail += f" (Número de filas: {len(df)})"
        raise HTTPException(status_code=400, detail=error_detail)
    

#añade tests a la base de datos subiendo un csv
@test.post("/api/postal_codes/upload_csv", status_code=201)
async def upload_csv(file: UploadFile = File(...)):
    df = None
    try:
        file.file.seek(0)
        df = pd.read_csv(file.file)

        if df.empty:
            raise ValueError("El archivo CSV está vacío")

        # Filtrar y renombrar columnas
        column_mapping = {
            "COD_POSTAL": "post_code",
            "Censo_mascota_CP": "census"
        }

        df = df[list(column_mapping.keys())].rename(columns=column_mapping)

        # Verificar valores NaN antes de conversión
        print("Valores NaN en 'census':", df["census"].isna().sum())

        # Rellenar NaN con 0.0 y asegurarse de que census sea float
        df["census"] = df["census"].fillna(0.0).astype(float)

        # Filtrar por los censuss que sean mayores o iguales a 1
        df["census"] = df["census"].replace(0, 1)
        
        # Asegurar que 'post_code' sea string de 5 dígitos
        df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

        print("Estructura final del DataFrame antes de la inserción:")
        print(df.head())
        print(df.dtypes)

        data_to_insert = df.to_dict(orient="records")

        with engine.connect() as conn:
            conn.execute(pc.insert().values(data_to_insert))
            conn.commit()

        return {"message": "Datos insertados correctamente", "total": len(data_to_insert)}

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío o no tiene contenido válido")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el CSV, verifica el formato del archivo")
    except Exception as e:
        error_detail = f"Error procesando el archivo CSV: {str(e)}"
        if df is not None:
            error_detail += f" (Número de filas: {len(df)})"
        raise HTTPException(status_code=400, detail=error_detail)

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

@test.post("/api/aemet/fill_db")
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

@test.post("/api/aemet/get_data")
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


scheduler.add_job(
    fill_db_aemet,
    IntervalTrigger(days=15),
    #IntervalTrigger(minutes=1),
    id="fill_db_aemet_job",
    replace_existing=True,
    max_instances=1
)

scheduler.start()