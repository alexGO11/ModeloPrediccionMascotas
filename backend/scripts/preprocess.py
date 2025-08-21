import pandas as pd

# Limpia el CSV de datos de mascotas
def prepare_test_data(data):
    column_mapping = {
        "Country": "country",
        "Pet sex": "sex",
        "Postal code": "post_code",
        "City": "city",
        "Geo Location": "location",
        "Value test": "result",
        "Pet age": "age",
        "Date": "date_done",
        "Name test": "disease"
    }
    
    # Definir el diccionario de mapeo
    value_test_mapping = {
        'Negativo': 0,
        'Positivo': 1,
        'Positivo Fuerte': 1
    }

    # Renombrar las columnas
    data = data.rename(columns=column_mapping)

    # Eliminar columnas innecesarias
    data = data.drop(columns=["location", "country"], errors="ignore")

    # Convertir la columna 'date_done' a formato de fecha
    data["date_done"] = pd.to_datetime(
        data["date_done"]
            .astype(str) 
            .str.replace('\ufeff', '', regex=True)  # Eliminar el BOM
            .str.replace('"', '', regex=True)       # Eliminar comillas extra
            .str.strip(),                           # Eliminar espacios en blanco
        errors='coerce'  # Si no se puede convertir, poner NaT
    )

    # Eliminar filas donde 'date_done' no pudo convertirse correctamente
    data = data.dropna(subset=["date_done"])

    # Filtrar solo valores válidos en 'result'
    valores_validos = list(value_test_mapping.keys())
    data = data[data["result"].isin(valores_validos)]

    # Mapear valores en 'result' (de 'Negativo' a 0 y 'Positivo' a 1)
    data["result"] = data["result"].map(value_test_mapping)

    # Asegurar que los valores en 'result' sean enteros
    data["result"] = data["result"].astype(int)

    # Asegurar que 'id_test' no tenga valores NaN y sea string
    if "id_test" in data.columns:
        data["id_test"] = data["id_test"].astype(str).fillna("")
        
    # Asegurar que 'post_code' sea string de 5 dígitos
    data["post_code"] = data["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

    # Asegurar que 'post_code' y 'age' sean enteros (si hay valores NaN, poner 0)
    data["post_code"] = data["post_code"].fillna(0).astype(int)

    # Limpia la columna 'age' para eliminar el patrón 'Año/s' y manejar valores faltantes o inválidos
    data["age"] = data["age"].str.extract(r"(\d+)")
    data["age"] = pd.to_numeric(data["age"], errors="coerce")
    data["age"] = data["age"].fillna(0).astype(int)

    # Reemplazar valores nulos en la columna 'city' con 'desconocido'
    data["city"] = data["city"].fillna("desconocido")

    # Reemplazar valores nulos en la columna 'sex' con 'desconocido'
    data["sex"] = data["sex"].fillna("desconocido")


    # Eliminar filas donde 'post_code', 'date_done' o 'disease' sean NaN
    required_columns = ["post_code", "date_done", "disease", "result"]
    data = data.dropna(subset=required_columns)

    print("Datos preparados:")
    print(data.head())

    return data

def prepare_post_code_data(data):
    # Filtrar y renombrar columnas
    column_mapping = {
        "COD_POSTAL": "post_code",
        "Censo_mascota_CP": "census"
    }

    data = data[list(column_mapping.keys())].rename(columns=column_mapping)

    # Verificar valores NaN antes de conversión
    print("Valores NaN en 'census':", data["census"].isna().sum())

    # Rellenar NaN con 0.0 y asegurarse de que census sea float
    data["census"] = data["census"].fillna(0.0).astype(float)

    # Filtrar por los censuss que sean mayores o iguales a 1
    data["census"] = data["census"].replace(0, 1)
    
    # Asegurar que 'post_code' sea string de 5 dígitos
    data["post_code"] = data["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)

    return data


def prepare_aemet_data(registros, next_date, df_coords):
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
        return

    df_agg = df_aemet.groupby(["indicativo", "location"]).agg(
        temp=("temp", "mean")
    ).reset_index()
    df_agg["date"] = current_date.strftime("%Y-%m-%d")

    df_merged = pd.merge(df_agg, df_coords[["indicativo", "lat", "lon"]], on="indicativo", how="inner")
    df_merged.dropna(subset=["lat", "lon"], inplace=True)

    return df_merged

# Función para parsear coordenadas
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
        print(f"AEMET_ROUTES| Error en la conversión de coordenadas: {e}")
        return None