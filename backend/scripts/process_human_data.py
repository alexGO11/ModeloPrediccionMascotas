import pandas as pd

def prepare_human_data(data):
    
    columns = ["Post Code", "Disease", "Date"]
    df_filtered = data[columns]

    df_filtered = df_filtered.dropna(subset=columns)
    
    df_filtered["Disease"] = df_filtered["Disease"].str.replace(r".*Leishman.*", "Leishmania", regex=True)
    
    df_filtered = df_filtered.rename(columns={
        "Post Code": "post_code",
        "Disease": "disease",
        "Date": "date"
    })
    
    df_filtered['date'] = pd.to_datetime(df_filtered['date'], errors='coerce')

    df_filtered['date'] = df_filtered['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    
    return df_filtered