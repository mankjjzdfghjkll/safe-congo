import pandas as pd
import unicodedata

def normalize(s):
    if not isinstance(s, str):
        s = str(s)
    s = s.strip().casefold()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s

df = pd.read_csv('data/processed/donnees_agregees_nettoyees.csv')

provinces = sorted({str(p).strip() for p in df['PROVINCE'].dropna() if str(p).strip() and str(p).strip().lower() != 'nan'})

for prov in provinces:
    norm_prov = normalize(prov)
    mask = df['PROVINCE'].astype(str).apply(normalize) == norm_prov
    zones = df.loc[mask, 'ZONE_SANTE'].dropna().astype(str).str.strip().unique()
    print(f"Province: {prov} ({len(zones)} zones)")
    for z in list(zones)[:5]:
        print(f"   - {z}")
    if len(zones) > 5:
        print(f"   ... ({len(zones)-5} autres)")
    print()
