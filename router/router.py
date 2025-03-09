from fastapi import APIRouter, Response, UploadFile, File, HTTPException, Query
from starlette.status import HTTP_201_CREATED
from schema.test_schema import TestSchema
import pandas as pd
from sqlalchemy import select, and_
from datetime import datetime
from config.db import engine
from model.tests import tests
from typing import List
from preprocess import clean_csv

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
    with engine.connect() as conn:
        stmt = select(tests).limit(limit).offset(offset)
        result = conn.execute(stmt).fetchall()

        
        return [dict(row) for row in result]

#obtiene los tests filtrando por fecha y tipo de enfermedad
@test.get("/api/test/{date}/{desease}", response_model=List[TestSchema])
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
        return [dict(row) for row in result]


#crea un test individual
@test.post("/api/test", status_code=HTTP_201_CREATED)
def create_user(data_test: TestSchema):
    with engine.connect() as conn:
        new_test = data_test.dict()
        conn.execute(tests.insert().values(new_test))
        return Response(status_code=HTTP_201_CREATED)
    

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

        data_to_insert = df.to_dict(orient="records")

        with engine.connect() as conn:
            conn.execute(tests.insert().values(data_to_insert))

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

@test.put("/api/test")
def update_user():
    pass