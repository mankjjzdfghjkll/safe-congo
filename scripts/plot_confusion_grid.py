"""
Plot a well-structured grid of confusion matrices found under `models/evaluation`.
Saves PNG to `models/evaluation/figure_3_8_alt.png` and `rapport/images/figure_3_8_alt.png`.
If no real CSVs are found, the script creates demo confusion matrices.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

EVAL_DIR = Path(__file__).resolve().parent.parent / 'models' / 'evaluation'
OUT1 = EVAL_DIR / 'figure_3_8_alt.png'
OUT2 = Path(__file__).resolve().parent.parent / 'rapport' / 'images' / 'figure_3_8_alt.png'
OUT2.parent.mkdir(parents=True, exist_ok=True)


def load_confusion_files(eval_dir: Path):
    files = sorted(eval_dir.glob('*_confusion_matrix.csv'))
    mats = []
    names = []
    for f in files:
        try:
            df = pd.read_csv(f, index_col=0)
            # ensure numeric matrix
            mat = df.values.astype(float)
            labels = list(df.index.astype(str))
            mats.append((mat, labels, f.name.replace('_confusion_matrix.csv', '')))
            names.append(f.name)
        except Exception:
            continue
    return mats


def demo_matrices():
    rng = np.random.default_rng(0)
    mats = []
    diseases = ['Choléra', 'Paludisme', 'COVID-19']
    for name in diseases:
        # build a plausible confusion matrix for 3 severity classes: Low/Med/High
        base = rng.integers(20, 200, size=(3, 3))
        # increase diagonal to simulate sensible models
        base = base + np.diag([300, 200, 100])
        mats.append((base, ['Low', 'Med', 'High'], name))
    return mats


def plot_grid(mats, title='Figure 3.8 (alternative): Matrices de confusion de sévérité'):
    n = len(mats)
    cols = min(3, n)
    rows = (n + cols - 1) // cols

    # compute global vmin/vmax for consistent colormap
    all_vals = np.concatenate([m[0].ravel() for m in mats])
    vmin, vmax = all_vals.min(), all_vals.max()

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    if rows * cols == 1:
        axes = np.array([[axes]])
    axes = np.atleast_2d(axes)

    for i, (mat, labels, name) in enumerate(mats):
        r = i // cols
        c = i % cols
        ax = axes[r, c]
        sns.heatmap(mat, annot=True, fmt='g', cmap='Blues', cbar=True,
                    vmin=vmin, vmax=vmax, ax=ax, linewidths=0.5, linecolor='gray')
        ax.set_title(name, fontsize=12)
        ax.set_xlabel('Prédiction')
        ax.set_ylabel('Référence')
        ax.set_xticks(np.arange(len(labels)) + 0.5)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticks(np.arange(len(labels)) + 0.5)
        ax.set_yticklabels(labels, rotation=0)

        # add normalized percentages as small text under counts
        totals = mat.sum(axis=1, keepdims=True)
        with np.errstate(divide='ignore', invalid='ignore'):
            pct = np.divide(mat, totals) * 100
            pct = np.nan_to_num(pct)
        for ii in range(mat.shape[0]):
            for jj in range(mat.shape[1]):
                ax.text(jj + 0.5, ii + 0.7, f"{pct[ii, jj]:.1f}%",
                        color='black', ha='center', fontsize=8, alpha=0.8)

    # hide unused axes
    total_axes = rows * cols
    for k in range(n, total_axes):
        r = k // cols
        c = k % cols
        axes[r, c].axis('off')

    fig.suptitle(title, fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


if __name__ == '__main__':
    mats = load_confusion_files(EVAL_DIR)
    if not mats:
        mats = demo_matrices()
        print('No confusion CSVs found, using demo matrices')
    else:
        print(f'Found {len(mats)} confusion matrices')

    fig = plot_grid(mats)
    fig.savefig(OUT1, dpi=200)
    fig.savefig(OUT2, dpi=200)
    print('Saved images to:', OUT1, OUT2)
