import pandas as pd
import time
import tqdm

raw = pd.read_csv('data/new_data.csv')

df_groupby = raw.groupby(['Postal code']).agg(
    n_positives=('Value test', lambda x: (x == 'Positivo').sum()),
    city = ('City', 'first')
).reset_index()

df_groupby['Postal code'] = df_groupby['Postal code'].astype(int)   
df_groupby["Postal code"] = df_groupby["Postal code"].astype(str).str.zfill(5)

df_groupby.to_csv('data/grouped_pc.csv', index=False)
