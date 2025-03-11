import pandas as pd

# Cargar los datos desde un archivo CSV
archivo_csv = 'data/raw/censo.csv'  # Reemplazar con el nombre real del archivo
df = pd.read_csv(archivo_csv)

# Filtrar solo las columnas necesarias
df = df[['COD_POSTAL', 'Censo_mascota_CP', 'area_cp']]

# Calcular el censo estimado para los códigos postales con censo 0
censo_total = df['Censo_mascota_CP'].sum()
area_total = df.loc[df['Censo_mascota_CP'] > 0, 'area_cp'].sum()  # Área solo donde hay censo

# Estimar densidad poblacional general
densidad_media = censo_total / area_total if area_total > 0 else 0

def estimar_censo(row):
    """Si el censo es 0, calcularlo en base al área y la densidad promedio."""
    if row['Censo_mascota_CP'] == 0 and row['area_cp'] > 0:
        return row['area_cp'] * densidad_media
    return row['Censo_mascota_CP']

# Aplicar el cálculo
if densidad_media > 0:
    df['Censo_mascota_CP'] = df.apply(estimar_censo, axis=1)

# Guardar el resultado en un nuevo archivo CSV
df.to_csv('codigos_postales_procesados.csv', index=False)

print("Archivo procesado y guardado como 'codigos_postales_procesados.csv'")