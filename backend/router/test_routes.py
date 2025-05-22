from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
import pandas as pd
import json
from sqlalchemy import select, and_
from datetime import datetime, timedelta

from config.db_connection import engine
from model.tests import tests
from scripts.preprocess import clean_csv
from scripts.getisord import aply_getisord
from model.postal_code import pc

test_routes = APIRouter()

@test_routes.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

# obtiene un intervalo de tiempo para buscar en la base de datos, aplica getisord a cada intervalo y devuelve una lista de geoJSONS
@test_routes.post("/api/test/filtered")
async def get_tests_filtered(request: Request):
    raw_body = await request.body()

    try:
        params = json.loads(raw_body.decode("utf-8"))  # Decodifica y convierte a diccionario
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "El cuerpo de la solicitud no es un JSON válido"}, status_code=400)

    print("Datos recibidos:", params)  # Debugging

    # Verificar si la clave "start_date" existe
    if "start_date" not in params:
        return {"Error": "Falta el parámetro start_date en el JSON"}

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
@test_routes.post("/api/test/upload_csv", status_code=201)
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