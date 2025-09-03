from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse

import pandas as pd
import json
from sqlalchemy import select, and_
from datetime import datetime, timedelta, timezone

from model.precalculated import precalculated
from config.db_connection import engine
from model.tests import tests
from scripts.preprocess import prepare_test_data
from scripts.getisord import apply_getisord
from model.post_code import pc

from scripts.serialize_geojson import serialize_geojson_rows

test_routes = APIRouter()

# List of prelimated time intervals and diseases
# These are the time intervals that can be requested directly without calculating them
intervals = [15, 30, 60, 90, 120]
diseases = ["Leishmania", "Giardia"]

@test_routes.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

# Receive a time interval introduced by the user and returns the data of all the tests separated by time intervals
@test_routes.post("/filtered")
async def get_tests_filtered(request: Request):
    
    raw_body = await request.body()

    try:
        params = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "El cuerpo no es JSON válido"}, status_code=400)

    print("TEST_ROUTES| Datos recibidos:", params)

    # Initialize variables
    start_date = datetime.now(timezone.utc)
    end_date = datetime.strptime("2022-01-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
    interval = params["interval"]
    disease = params["disease"]

    # If the interval coincides with the precalculated ones, return them
    if interval in intervals:

        print("TEST_ROUTES| Intervalo de tiempo precalculado encontrado:", interval)

        with engine.connect() as conn:
            query = select(precalculated).where(
                and_(
                    precalculated.c.days_interval == f"{interval}D",
                    precalculated.c.disease == disease
                )
            ).order_by(precalculated.c.end_date.desc())

            result = conn.execute(query)
            rows = result.fetchall()

            print("TEST_ROUTES| Datos precalculados encontrados:", len(rows))

            geojson = serialize_geojson_rows(rows)

            print("TEST_ROUTES| GeoJSON generado")

            return JSONResponse(content=geojson)

    # If there are no prealculated data, calculate them manually
    results = []

    with engine.connect() as conn:
        print("TEST_ROUTES| Conexion a la base de datos realizada")
        current_date = start_date

        census_db = conn.execute(select(pc))
        census = pd.DataFrame(census_db.fetchall(), columns=census_db.keys())

        # Tour all dates with temporary jumps = to the interval
        while current_date >= end_date:
            next_date = current_date - timedelta(days=interval)

            query = select(tests).where(
                and_(
                    tests.c.date_done <= current_date,
                    tests.c.date_done > next_date,
                    tests.c.disease == disease
                )
            )

            result = conn.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

            # If there is data, apply the Getis-Uord algorithm and the results are added to the list
            if not df.empty:
                df_resultado = apply_getisord(df, census)

                results.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "geojson": df_resultado
                })

            current_date = next_date

    return JSONResponse(content=results)

# Generates preliminary data for all time and disease intervals
@test_routes.post("/precalculated", status_code=status.HTTP_201_CREATED)
async def create_precalculated_data():
    try:
        # Clean the table before inserting new data and obtaining the census
        with engine.connect() as conn:
            trans = conn.begin()
            conn.execute(precalculated.delete())  
            query = select(pc)
            census_db = conn.execute(query)
            trans.commit()
            census = pd.DataFrame(census_db.fetchall(), columns=census_db.keys())
            conn.commit()

        start_date = datetime.utcnow()
        end_date = datetime.strptime("2022-01-01", "%Y-%m-%d")
        print("End date:", end_date)

        current_date = start_date

        # For each time and disease interval, the data is obtained and we apply Getis-Pord and then store the results in the database
        for interval in intervals:
            current_date = start_date
            while current_date >= end_date:
                for disease in diseases:
                    print(f"Procesando enfermedad: {disease} con intervalo: {interval} días")
                    with engine.connect() as conn:
                        trans = conn.begin()
                        print("Conectado a la base de datos")
                        
                        print("Current date:", current_date)
                        next_date = current_date - timedelta(days=interval)
                        print("Start date:", start_date)
                        print("Next date:", next_date)
                        print("Interval:", interval)

                        # Query filtering for the current time interval
                        query = select(tests).where(
                                and_(
                                    tests.c.date_done <= current_date,
                                    tests.c.date_done > next_date,
                                    tests.c.disease == disease
                                )
                            )
                        print("Query:", query)
                        result = conn.execute(query)
                        trans.commit()
                        df = pd.DataFrame(result.fetchall(), columns=result.keys())
                        df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)
                            
                        try:
                            df_resultado = apply_getisord(df, census)
                            # If the result is empty it is filled with empty json
                            if not df_resultado or not df_resultado.get("features"):  # Void or without features
                                print("GeoJSON vacío, insertando estructura mínima")
                                df_resultado = {"type": "FeatureCollection", "features": []}

                            # Eliminate geometry to facilitate stored in the database
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
                            trans.commit()
                        except Exception as e:
                            print("Fallo al insertar:", e)
                        conn.commit()
                        
                        current_date = next_date
                
        return {"message": "Datos precalculados insertados correctamente"}
    except Exception as e:
        trans.rollback()
        print("Error al insertar datos precalculados:", e)
        return JSONResponse(
            content={"error": f"Error al procesar la solicitud: {str(e)}"},
            status_code=500,
        )

#Add tests to the database uploading a CSV
@test_routes.post("/upload_csv", status_code=201)
async def upload_csv(file: UploadFile = File(...)):
    df = None
    try:
        file.file.seek(0)

        df = pd.read_csv(file.file)

        if df.empty:
            raise ValueError("TEST_ROUTES| El archivo CSV está vacío")

        print("TEST_ROUTES| Preparando datos...")

        df = prepare_test_data(df)
        df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

        data_to_insert = df.to_dict(orient="records")

        with engine.connect() as conn:
            conn.execute(tests.insert().values(data_to_insert))
            conn.commit()
            
        # We generate new prealculated data
        create_precalculated_data()

        return {"message": "Datos insertados correctamente", "total": len(data_to_insert)}

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío o no tiene contenido válido")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el CSV, verifica el formato del archivo")
    except Exception as e:
        error_detail = f"TEST_ROUTES| Error procesando el archivo CSV: {str(e)}"
        if df is not None:
            error_detail += f" (Número de filas: {len(df)})"
        raise HTTPException(status_code=400, detail=error_detail)