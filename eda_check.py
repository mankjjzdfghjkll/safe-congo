import pandas as pd
from pathlib import Path
from src.pipeline.data_cleaner import DataCleaner

base = Path('.')
cleaner = DataCleaner(
    str(base / 'data/raw/drc-2023_sem08.xlsx'),
    str(base / 'data/raw/drc-2022_sem40.xlsx')
)

raw = cleaner.load_data()
print('\n[EDA RAW]')
print('shape =', raw.shape)
raw_dates = pd.to_datetime(raw['DEBUTSEM'], errors='coerce')
print('date_min =', raw_dates.min(), '| date_max =', raw_dates.max())
print('missing_top =', raw.isna().sum().sort_values(ascending=False).head(8).to_dict())
print('disease_nunique =', raw['MALADIE'].nunique())
print('top_diseases =', raw['MALADIE'].value_counts().head(10).to_dict())

cleaner.clean_data()
df = cleaner.cleaned_data
dates = pd.to_datetime(df['DEBUTSEM'], errors='coerce')

print('\n[EDA CLEAN]')
print('shape =', df.shape)
print('date_min =', dates.min(), '| date_max =', dates.max())
years = sorted(dates.dt.year.dropna().unique().tolist())
print('years_head =', years[:10])
print('years_tail =', years[-10:])
print('rows_year_2102 =', int((dates.dt.year == 2102).sum()))
key_cols = [k for k in ['DEBUTSEM', 'MALADIE', 'ZS', 'PROV'] if k in df.columns]
print('dupes_key =', int(df.duplicated(subset=key_cols).sum()))
print('totalcas_desc =', df['TOTALCAS'].describe(percentiles=[0.5, 0.9, 0.95, 0.99]).to_dict())
