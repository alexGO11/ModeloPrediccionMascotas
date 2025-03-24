from fastapi import APIRouter, Response, Request, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED
from schema.test_schema import TestSchema
from schema.pc_schema import PostalCodeSchema
import pandas as pd
import numpy as np
import json
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from config.db import engine
from model.tests import tests
from typing import List
from scripts.preprocess import clean_csv
from scripts.getisord import aply_getisord
from model.postal_code import pc
from model.getisord_t import getis_ord

test = APIRouter()

@test.get("/")
def root():
    return {"message": "hi im fastAPI with a router"}

#obtiene todos los tests en la base de datos
@test.get("/api/test", response_model=List[TestSchema])
def get_tests(
    #parametros de paginacion para no saturar la api
    limit: int = Query(10, ge=1, le=100),  # Número máximo de registros por página (por defecto 10, máximo 100)
    offset: int = Query(0, ge=0)           # Desde qué registro empezar la consulta
):
    try:
        with engine.connect() as conn:
            stmt = select(tests).limit(limit).offset(offset)
            result = conn.execute(stmt).fetchall()
            conn.commit()
            print("conectado a la base de datos", result)
            return result
    except Exception as e:
        print("Error al conectar:", e)

#obtiene los tests filtrando por fecha y tipo de enfermedad
"""@test.get("/api/test/{date}/{desease}", response_model=List[TestSchema])
def get_tests(
    date: datetime, 
    desease: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)           
    ):
    
    with engine.connect() as conn:
        today = datetime.today().date()
        # Filtrar por fecha y enfermedad con paginación
        stmt = (
            select(tests)
            .where(
                and_(
                    tests.c.date_done.between(date, today),
                    tests.c.desease == desease
                )
            )
            .limit(limit)
            .offset(offset)
        )
        result = conn.execute(stmt).fetchall()
        return [dict(row) for row in result]"""

     
@test.get("/api/test/{date}/{desease}")
def get_tests(
    date: datetime, 
    desease: str,
    limit: int = Query(100, ge=1, le=500), 
    offset: int = Query(0, ge=0)  
    ):

    with engine.connect() as conn:
        all_results = []

        while True:
            # Construir la consulta paginada
            query = (
                select(tests)
                .where(
                    and_(
                        tests.c.date_done >= date,
                        tests.c.desease == desease
                    )
                )
                .limit(limit)
                .offset(offset)
            )

            result = conn.execute(query)
            rows = result.fetchall()
            if not rows:
                break  # Salir del bucle si no hay más datos
            
            all_results.extend(rows)  # Agregar resultados a la lista
            offset += limit  # Incrementar el offset para la siguiente consulta

        # Convertir los resultados a DataFrame
        if not all_results:
            return {"message": "No hay datos para los parámetros proporcionados"}

        df = pd.DataFrame(all_results, columns=result.keys())

        # Aplicar la función de análisis espacial
        df_resultado = aply_getisord(df)
        
        
        geojson_result = df_resultado.to_json()

        print(df_resultado.head())
        
        # calcular centroides y devolver geoJSON
        return geojson_result
    
"""@test.post("/api/test/filtered")
async def get_tests_filtered(request: Request):
    params = await request.json()
    date = params["date"]
    desease = params["desease"]

    with engine.connect() as conn:
        query = select(tests).where(
            and_(
                tests.c.date_done >= date,
                tests.c.desease == desease
            )
        ).limit(500)  # Limita la cantidad de datos devueltos

        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Aplica análisis espacial
        df_resultado = aply_getisord(df)
        # Convertir todos los datos de numpy a tipos nativos de Python
        df_resultado = df_resultado.applymap(lambda x: x.item() if isinstance(x, (np.integer, np.floating)) else x)

        # Convertir a GeoJSON
        geojson_result = df_resultado.to_json()

        # Enviar respuesta JSON
        return JSONResponse(content=json.loads(geojson_result))"""
        
# obtiene un intervalo de tiempo para buscar en la base de datos, aplica getisord a cada intervalo y devuelve una lista de geoJSONS
@test.post("/api/test/filtered")
async def get_tests_filtered(request: Request):
    raw_body = await request.body()
    params = raw_body.decode("utf-8")  # Decodifica el JSON en UTF-8
    
    print("Datos recibidos:", params)  # Debugging

    # Verificar si la clave "start_date" existe
    if "start_date" not in params:
        return {"error": "Falta el parámetro start_date en el JSON"}

    try:
        start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
        return {"message": "Fecha procesada correctamente", "start_date": str(start_date)}
    except Exception as e:
        return {"error": f"Error al procesar start_date: {str(e)}"}

    start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")
    interval = params["interval"]
    desease = params["desease"]

    results = []
    
    with engine.connect() as conn:
        current_date = start_date
        
        query = select(pc)

        census_db = conn.execute(query)
        census = pd.DataFrame(census_db.fetchall(), columns=census_db.keys())
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=interval)
            print("Start date:", start_date)
            print("Next date:", next_date)
            print("Interval:", interval)

            # Consulta filtrando por el intervalo de tiempo actual
            query = select(tests).where(
                and_(
                    tests.c.date_done >= current_date,
                    tests.c.date_done < next_date,
                    tests.c.desease == desease
                )
            )

            result = conn.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)
            
            if not df.empty:
                df_resultado = aply_getisord(df, census)  # Genera GeoJSON

                results.append({
                    "date": current_date.strftime("%Y-%m-%d"),  
                    "geojson": df_resultado
                })

            current_date = next_date

    return JSONResponse(content=results)



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
