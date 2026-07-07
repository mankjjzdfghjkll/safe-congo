from pathlib import Path
src = Path('models') / 'evaluation' / 'confusion_matrices_combined.png'
dst_dir = Path.home() / 'Desktop' / 'capture memoire'
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / src.name

with src.open('rb') as fsrc:
    data = fsrc.read()
with dst.open('wb') as fdst:
    fdst.write(data)

print('copied', src, '->', dst)
