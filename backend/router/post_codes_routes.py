from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from config.db_connection import engine
from model.postal_code import pc

post_codes_routes = APIRouter()

#añade tests a la base de datos subiendo un csv
@post_codes_routes.post("/upload_csv", status_code=201)
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