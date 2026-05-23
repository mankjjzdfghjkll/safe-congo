import pandas as pd
import os

path = 'data/raw/drc-2022_sem40.xlsx'
print('Taille fichier:', round(os.path.getsize(path)/1024/1024, 2), 'MB')

df22 = pd.read_excel(path, nrows=10)
print('Colonnes:', list(df22.columns))
print(df22.to_string())

