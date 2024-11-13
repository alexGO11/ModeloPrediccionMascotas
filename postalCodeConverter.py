import pandas as pd
import time
import tqdm

raw = pd.read_csv('20241031_reporting.csv')
df_postal = pd.read_csv('postal_codes.csv')

pc_serie = pd.Series(df_postal.iloc[:, 0])

df_groupby = raw.groupby(['Postal code']).agg(
    n_positives=('Value test', lambda x: (x == 'Positivo').sum()),
    city = ('City', 'first')
).reset_index()

df_groupby['Postal code'] = df_groupby['Postal code'].astype(int)   

df_groupby.to_csv('grouped_pc.csv', index=False)

pbar = tqdm.trange(100,desc="Exportando...")
for i in range(10):
    pbar.update(n=10)
    time.sleep(0.1)
pbar.close()