"""
Extract text from all PDFs in the teoria folder using PyMuPDF.
"""
import fitz  # PyMuPDF
import os

folder = "C:\\Users\\rocel\\OneDrive\\Desktop\\compressibilidade z\\material\\teoria\\mat\u00e9ria completa"

priority = [
    "Aula 4_SALADEAULAINVERTIDAEnRES1 2025_2026_cap2.pdf",
    "SALA DE AULA INVERTIDA_Aula 1_ 2025_2026 - INTRODUÇÃO À ENG RESER 1 (1).pdf",
    "SALA DE AULA INVERTIDA_Aula 2_2025_2026 - INTRODUÇÃO À ENG RESER 1 (1).pdf",
    "SALA DE AULA INVERTIDA_Aula 2_2025_2026 - INTRODUÇÃO À ENG RESER 1 (2).pdf",
    "Tarefas de Engenharia de Reservatórios I 2024.pdf",
]

out_dir = r"C:\Users\rocel\OneDrive\Desktop\compressibilidade z\material\teoria"

for fname in priority:
    path = os.path.join(folder, fname)
    if not os.path.exists(path):
        print(f"NOT FOUND: {fname}")
        continue
    out_name = (fname[:55] + ".txt").replace(" ", "_")
    out_path = os.path.join(out_dir, out_name)
    print(f"Extracting: {fname[:60]}")
    try:
        doc = fitz.open(path)
        pages_text = []
        for i, page in enumerate(doc):
            t = page.get_text()
            pages_text.append(f"\n\n=== PAGE {i+1} ===\n{t}")
        full_text = "".join(pages_text)
        doc.close()
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"  -> {len(full_text)} chars, {len(pages_text)} pages")
    except Exception as e:
        print(f"  ERROR: {e}")
print("Done.")
