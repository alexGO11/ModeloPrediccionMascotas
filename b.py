import pandas as pd

# Cargar los archivos CSV
df_positivos = pd.read_csv("data/processed/grouped_data.csv")
df_censo = pd.read_csv("data/raw/censo.csv")

df_censo = df_censo.rename(columns={"COD_POSTAL": "post_code"})

# Unir los datos por 'codigo_postal'
df_merged = pd.merge(df_positivos, df_censo, on='post_code', how='left')
     
# Filtrar los casos donde el censo es 0 pero hay positivos
df_resultado = df_merged[(df_merged['Censo_mascota_CP'] == 0) & (df_merged['casos_positivos'] > 0)]
    
# Mostrar los resultados
if not df_resultado.empty:
    print("Códigos postales con censo 0 y casos positivos:")
    print(df_resultado)
else:
    print("No hay códigos postales con censo 0 y positivos registrados.")