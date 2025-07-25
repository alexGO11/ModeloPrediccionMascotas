from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
import pandas as pd
import json
from sqlalchemy import select, and_
from datetime import datetime, timedelta

from model.precalculated import precalculated

from config.db_connection import engine
from model.tests import tests
from scripts.preprocess import clean_csv
from scripts.getisord import aply_getisord
from model.postal_code import pc

from scripts.serialize_geojson import serialize_geojson_rows

test_routes = APIRouter()

# Lista de intervalos de tiempo precalculados y enfermedades
# Estos son los intervalos de tiempo que se pueden solicitar directamente sin necesidad de calcularlos
intervals = [15, 30, 60, 90, 120]
diseases = ["Leishmania", "Giardia"]

@test_routes.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

# Recibe un intervalo de tiempo introducido por el usuario y devuelve los datos de todos los tests realizados separados por intervalos de tiempo
@test_routes.post("/api/test/filtered")
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
    if interval in intervals:
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

            print("GeoJSON generado:", geojson)

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
@test_routes.post("/api/test/precalculated", status_code=status.HTTP_201_CREATED)
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
                    print(f"Procesando enfermedad: {disease} con intervalo: {interval} días")
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