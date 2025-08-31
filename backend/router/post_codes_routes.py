from fastapi import APIRouter, UploadFile, File, HTTPException

import pandas as pd
from config.db_connection import engine
from model.post_code import pc
from scripts.preprocess import prepare_post_code_data

post_codes_routes = APIRouter()

#añade tests a la base de datos subiendo un csv
@post_codes_routes.post("/upload_csv", status_code=201)
async def upload_csv(file: UploadFile = File(...)):
    df = None
    try:
        file.file.seek(0)
        df = pd.read_csv(file.file)

        if df.empty:
            raise ValueError("POST_CODES_ROUTES| El archivo CSV está vacío")

        print("POST_CODES_ROUTES| Preparando datos...")

        df_filtered = prepare_post_code_data(df)

        data_to_insert = df_filtered.to_dict(orient="records")

        print("POST_CODES_ROUTES| Insertando datos en la base de datos...")
        with engine.connect() as conn:
            conn.execute(pc.insert().values(data_to_insert))
            conn.commit()

        return {"message": "Datos insertados correctamente", "total": len(data_to_insert)}

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío o no tiene contenido válido")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al analizar el CSV, verifica el formato del archivo")
    except Exception as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="POST_CODES_ROUTES| La base de datos ya está llena con los datos.")
        
        error_detail = f"POST_CODES_ROUTES| Error procesando el archivo CSV: {str(e)}"
        if df is not None:
            error_detail += f" (Número de filas: {len(df)})"
        raise HTTPException(status_code=400, detail=error_detail)