"""
Plot weekly time series for the top-5 diseases (by total cases) between 2021 and 2023.
Saves high-resolution PNG to project folder and copies to Desktop 'capture memoire'.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parent.parent
PROC_DIR = BASE / 'data' / 'processed'
OUT_FILE = BASE / 'rapport' / 'images' / 'figure_3_6_top5.png'
DST_DIR = Path.home() / 'Desktop' / 'capture memoire'
DST_DIR.mkdir(parents=True, exist_ok=True)

# try candidate files
candidates = [PROC_DIR / 'dataset_propre.csv', PROC_DIR / 'dataset_propre_check.csv', PROC_DIR / 'aggregated_data.csv', BASE / 'data' / 'processed' / 'donnees_agregees_nettoyees.csv']
df = None
for c in candidates:
    if c.exists():
        try:
            df = pd.read_csv(c, parse_dates=['Date_debut'], dayfirst=True)
            print('Loaded', c)
            break
        except Exception:
            try:
                df = pd.read_csv(c, parse_dates=['DEBUTSEM'], dayfirst=True)
                df.rename(columns={'DEBUTSEM':'Date_debut'}, inplace=True)
                print('Loaded', c, 'as DEBUTSEM')
                break
            except Exception:
                continue

if df is None:
    raise SystemExit('No processed CSV found in data/processed; cannot plot')

# Ensure column names and numeric
if 'TOTALCAS' not in df.columns and 'Total_cas' in df.columns:
    df['TOTALCAS'] = pd.to_numeric(df['Total_cas'], errors='coerce')
if 'MALADIE' not in df.columns and 'Maladie' in df.columns:
    df['MALADIE'] = df['Maladie']

# keep 2021-2023
df['Date_debut'] = pd.to_datetime(df['Date_debut'], errors='coerce')
df = df.dropna(subset=['Date_debut'])
df = df[(df['Date_debut'].dt.year >= 2021) & (df['Date_debut'].dt.year <= 2023)]

# aggregate if needed
if 'TOTALCAS' not in df.columns:
    # try other name
    cols = [c for c in df.columns if 'TOTAL' in c.upper()]
    if cols:
        df['TOTALCAS'] = pd.to_numeric(df[cols[0]], errors='coerce')
    else:
        raise SystemExit('No TOTALCAS column found')

agg = df.groupby(['Date_debut','MALADIE'], as_index=False).agg({'TOTALCAS':'sum'})

# identify top5 by total cases across period
totals = agg.groupby('MALADIE', as_index=False)['TOTALCAS'].sum().sort_values('TOTALCAS', ascending=False)
top5 = totals.head(5)['MALADIE'].tolist()
print('Top5 diseases:', top5)

# pivot weekly
# ensure weekly index (Date_debut already weekly start)
full_index = pd.date_range('2021-01-01','2023-12-31', freq='W-MON')
plot_df = pd.DataFrame(index=full_index)
for d in top5:
    s = agg[agg['MALADIE']==d].set_index('Date_debut').reindex(full_index)['TOTALCAS'].fillna(0)
    plot_df[d] = s

# smoothing: optional rolling mean
smooth = plot_df.rolling(window=3, min_periods=1, center=True).mean()

sns.set(style='whitegrid', context='talk')
plt.figure(figsize=(16,9), dpi=200)
palette = sns.color_palette('tab10', n_colors=len(top5))
for i, d in enumerate(top5):
    plt.plot(plot_df.index, plot_df[d], label=f'{d} (raw)', color=palette[i], alpha=0.25, linewidth=1)
    plt.plot(smooth.index, smooth[d], label=f'{d}', color=palette[i], linewidth=2.5)
    # annotate last value
    last = plot_df[d].iloc[-1]
    plt.text(plot_df.index[-1], smooth[d].iloc[-1], f' {int(last):,}', color=palette[i], fontsize=10, va='center')

plt.title('Évolution hebdomadaire des 5 maladies les plus fréquentes (2021–2023)', fontsize=18)
plt.xlabel('Semaine')
plt.ylabel('Nombre de cas (hebdomadaire)')
plt.legend(loc='upper left')
plt.xlim(pd.Timestamp('2021-01-01'), pd.Timestamp('2023-12-31'))
plt.tight_layout()
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_FILE, dpi=300)
plt.savefig(DST_DIR / OUT_FILE.name, dpi=300)
print('Saved:', OUT_FILE, 'and', DST_DIR / OUT_FILE.name)
