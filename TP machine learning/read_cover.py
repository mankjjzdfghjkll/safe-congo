import pdfplumber
files = [
    r'C:\Users\PC\Desktop\Documentation final POO.pdf',
    r'C:\Users\PC\Desktop\documentation du projet.pdf',
]
for f in files:
    try:
        pdf = pdfplumber.open(f)
        print(f'=== {f} ===')
        print(pdf.pages[0].extract_text())
        pdf.close()
    except Exception as e:
        print(f'ERR {f}: {e}')
