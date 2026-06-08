import pdfplumber
files = [
    r'C:\Users\PC\Desktop\TP03 AUDIT INFO MANKAND-JOSEE.pdf',
    r'C:\Users\PC\Desktop\tp 02 ml.pdf',
    r'C:\Users\PC\Desktop\TP N\u00b0 1 DE MACHINE LEARNING.pdf',
    r'C:\Users\PC\Desktop\Audit tp 1.pdf',
]
for f in files:
    try:
        pdf = pdfplumber.open(f)
        print(f'=== {f} ===')
        for i, p in enumerate(pdf.pages[:2]):
            print(f'-- page {i+1} --')
            print(p.extract_text())
        pdf.close()
    except Exception as e:
        print(f'ERREUR {f}: {e}')
