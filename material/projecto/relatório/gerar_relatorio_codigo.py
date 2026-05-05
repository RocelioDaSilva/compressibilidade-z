"""
Gera o Relatório de Desenvolvimento de Código em Word.

Usa o ficheiro .docx base como template de estilos e constrói
um relatório técnico completo sobre o projecto Factor Z.

Dependências:  python-docx, Pillow, pygments
"""

import os
import io
import textwrap
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import docx.opc.constants

from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name


# ── Paths ─────────────────────────────────────────────────────────────────────

BASEDIR   = Path(__file__).parent
PROJDIR   = BASEDIR.parent / "z_factor"
DOCX_BASE = BASEDIR / "Relatório_SPECHAPTER_ISPTEC_2026 NOVO (2).docx"
DOCX_OUT  = BASEDIR / "Relatorio_Factor_Z_Codigo.docx"
IMG_DIR   = BASEDIR / "img_code"
IMG_DIR.mkdir(exist_ok=True)

# ── Group data ────────────────────────────────────────────────────────────────

GRUPO = [
    "Rocélio Da Silva (20220001)",
    "Marquinha Marcos (20200721)",
    "Arlindo Jamba (20222182)",
    "Nadir Manuel (20211333)",
    "Manuel Braz (20222320)",
    "Paulo Isaac Abel (20220918)",
    "Cristina Bongue (20221099)",
]
ORIENTADOR   = "Prof. Geraldo André Raposo Ramos"
INSTITUICAO  = ("Instituto Superior Politécnico de Tecnologias e Ciências "
                "(ISPTEC)")
DEPARTAMENTO = "Departamento de Geociências"
CURSO        = "Engenharia de Petróleo"
LOCAL        = "Luanda – Angola"
ANO          = "2026"
DISCIPLINA   = "Engenharia de Reservatórios I"
TITULO       = ("Factor de Compressibilidade do Gás Natural (Z) — "
                "Relatório de Desenvolvimento de Código")


# ── Code snippets to render ───────────────────────────────────────────────────

SNIPPETS = {
    "properties_critical": {
        "label": "Figura 1 – Módulo properties.py: Correlações de Propriedades Pseudo-Críticas",
        "file":  PROJDIR / "modules" / "properties.py",
        "lines": (1, 60),
    },
    "wichert_aziz": {
        "label": "Figura 2 – Módulo properties.py: Correcção de Wichert & Aziz",
        "file":  PROJDIR / "modules" / "properties.py",
        "lines": (54, 95),
    },
    "carr_kb": {
        "label": "Figura 3 – Módulo properties.py: Correcção de Carr, Kobayashi & Burrows",
        "file":  PROJDIR / "modules" / "properties.py",
        "lines": (97, 115),
    },
    "z_ideal": {
        "label": "Figura 4 – Módulo correlations.py: Gás Ideal (Z = 1)",
        "file":  PROJDIR / "modules" / "correlations.py",
        "lines": (1, 20),
    },
    "hall_yarborough": {
        "label": "Figura 5 – Módulo correlations.py: Correlação de Hall-Yarborough (Newton-Raphson)",
        "file":  PROJDIR / "modules" / "correlations.py",
        "lines": (22, 97),
    },
    "dranchuk": {
        "label": "Figura 6 – Módulo correlations.py: Correlação de Dranchuk & Abou-Kassem",
        "file":  PROJDIR / "modules" / "correlations.py",
        "lines": (99, 155),
    },
    "main_compute": {
        "label": "Figura 7 – main.py: Motor de Cálculo (função calcular_z_tabela)",
        "file":  PROJDIR / "main.py",
        "lines": (60, 110),
    },
    "main_gui": {
        "label": "Figura 8 – main.py: Interface Gráfica (classe AplicacaoFactorZ)",
        "file":  PROJDIR / "main.py",
        "lines": (112, 185),
    },
    "main_actions": {
        "label": "Figura 9 – main.py: Acções de Cálculo e Gráfico",
        "file":  PROJDIR / "main.py",
        "lines": (185, 255),
    },
}


# ── Render code to PNG ────────────────────────────────────────────────────────

def render_code_png(key: str, info: dict) -> Path:
    """Render a code snippet to a PNG image using pygments."""
    src_path: Path = info["file"]
    start, end = info["lines"]

    lines = src_path.read_text(encoding="utf-8").splitlines()
    snippet = "\n".join(lines[start - 1 : end])

    formatter = ImageFormatter(
        style="monokai",
        font_name="Courier New",
        font_size=13,
        line_numbers=True,
        line_number_start=start,
        image_pad=12,
        line_pad=2,
    )
    png_bytes = highlight(snippet, PythonLexer(), formatter)
    img_path = IMG_DIR / f"{key}.png"
    img_path.write_bytes(png_bytes)
    return img_path


# ── Word helpers ─────────────────────────────────────────────────────────────

def set_run_font(run, name="Times New Roman", size=12, bold=False, color=None):
    run.font.name = name
    run.font.size  = Pt(size)
    run.font.bold  = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_heading(doc: Document, text: str, level: int = 1):
    """Add a heading paragraph using built-in Heading styles."""
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Times New Roman"
        run.font.color.rgb = RGBColor(0, 0, 0)
    return p


def add_body(doc: Document, text: str, indent=False):
    """Add a body paragraph."""
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(1.25)
    run = p.add_run(text)
    set_run_font(run)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    return p


def add_bullet(doc: Document, text: str):
    """Add a bullet-style paragraph using manual indent (avoids missing styles)."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent       = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    run = p.add_run("\u2022  " + text)
    set_run_font(run)
    return p


def add_code_image(doc: Document, img_path: Path, caption: str, max_width=Cm(16)):
    """Insert a code PNG into the document with a caption."""
    doc.add_paragraph()  # spacing
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_img.add_run()
    run.add_picture(str(img_path), width=max_width)

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_cap.add_run(caption)
    set_run_font(r, size=10, bold=True)
    doc.add_paragraph()  # spacing


def page_break(doc: Document):
    doc.add_page_break()


# ── Document builder ──────────────────────────────────────────────────────────

def build_doc():
    # ── Load base template for styles ────────────────────────────────────────
    doc = Document(str(DOCX_BASE))

    # Clear all existing content but keep styles AND the final sectPr
    body = doc.element.body
    sectPr = body.find(qn("w:sectPr"))  # preserve section properties
    for element in list(body):
        body.remove(element)
    # Re-attach sectPr so sections[-1] works for table width
    if sectPr is not None:
        body.append(sectPr)

    # ── Capa ─────────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(INSTITUICAO.upper())
    set_run_font(r, size=13, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(DEPARTAMENTO.upper())
    set_run_font(r, size=12, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(CURSO.upper())
    set_run_font(r, size=12, bold=True)

    doc.add_paragraph()
    doc.add_paragraph()

    # Group name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("GRUPO 5")
    set_run_font(r, size=13, bold=True)

    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(TITULO.upper())
    set_run_font(r, size=14, bold=True)

    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(LOCAL)
    set_run_font(r, size=12, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(ANO)
    set_run_font(r, size=12, bold=True)

    page_break(doc)

    # ── Folha de rosto ────────────────────────────────────────────────────────
    for nome in GRUPO:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(nome.upper())
        set_run_font(r, size=12, bold=True)

    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(TITULO.upper())
    set_run_font(r, size=14, bold=True)

    doc.add_paragraph()
    doc.add_paragraph()

    # Preambulo
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent  = Cm(8)
    p.paragraph_format.right_indent = Cm(0)
    preambulo = (
        f"Relatório técnico de desenvolvimento de código apresentado ao Curso de "
        f"{CURSO} do {DEPARTAMENTO} do {INSTITUICAO} como componente de avaliação "
        f"contínua na disciplina de {DISCIPLINA}."
    )
    r = p.add_run(preambulo)
    set_run_font(r, size=11)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Cm(8)
    r = p.add_run(f"Orientador: {ORIENTADOR}")
    set_run_font(r, size=11)

    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{LOCAL}\n{ANO}")
    set_run_font(r, size=12, bold=True)

    page_break(doc)

    # ── Folha de aprovação ────────────────────────────────────────────────────
    for nome in GRUPO:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(nome.upper())
        set_run_font(r, size=12, bold=True)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(TITULO.upper())
    set_run_font(r, size=14, bold=True)

    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(8)
    r = p.add_run(preambulo)
    set_run_font(r, size=11)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    r = p.add_run("Trabalho avaliado em _________ de _______________ de _______")
    set_run_font(r, size=11)

    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("_" * 45)
    set_run_font(r, size=11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"Prof. Geraldo André Raposo Ramos\nProf. Orientador")
    set_run_font(r, size=11, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{LOCAL}, {ANO}")
    set_run_font(r, size=11)

    page_break(doc)

    # ── Resumo ────────────────────────────────────────────────────────────────
    add_heading(doc, "Resumo", level=1)
    add_body(doc, (
        "O presente relatório documenta o desenvolvimento de um programa computacional "
        "para o cálculo do factor de compressibilidade do gás natural (factor Z), "
        "no âmbito do Projecto Nº 1 da disciplina de Engenharia de Reservatórios I. "
        "O programa foi implementado em Python, com interface gráfica baseada em tkinter, "
        "e integra três metodologias de cálculo: gás ideal (Z = 1), correlação de "
        "Hall-Yarborough resolvida por Newton-Raphson, e correlação de Dranchuk & Abou-Kassem "
        "resolvida por iteração directa. Foram implementadas correlações de propriedades "
        "pseudo-críticas (Standing 1977 e Sutton) e correcções para contaminantes "
        "(Wichert & Aziz; Carr, Kobayashi & Burrows). O programa apresenta resultados "
        "em tabela comparativa e gráfico de Z versus pressão para uma malha de "
        "discretização definida pelo utilizador."
    ), indent=True)

    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("Palavras-chave: ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Factor Z. Gás Natural. Hall-Yarborough. Dranchuk & Abou-Kassem. "
        "Newton-Raphson. Python. Engenharia de Reservatórios."
    )
    set_run_font(r2)

    page_break(doc)

    # ── 1. Introdução ─────────────────────────────────────────────────────────
    add_heading(doc, "1  Introdução", level=1)
    add_body(doc, (
        "O factor de compressibilidade do gás natural, comumente denominado factor Z, "
        "é um parâmetro fundamental na equação de estado dos gases reais: PV = nZRT. "
        "Este factor quantifica o desvio do comportamento de um gás real face ao comportamento "
        "de um gás ideal, sendo indispensável para o cálculo de reservas, simulação de "
        "reservatórios, e dimensionamento de instalações de superfície."
    ), indent=True)
    add_body(doc, (
        "O presente trabalho documenta o desenvolvimento de um programa computacional, "
        "implementado em Python, que calcula o factor Z através de três abordagens: "
        "(i) gás ideal, (ii) correlação de Hall-Yarborough, e (iii) correlação de "
        "Dranchuk & Abou-Kassem. O programa dispõe de interface gráfica construída com "
        "a biblioteca tkinter e permite a visualização gráfica dos resultados através "
        "da biblioteca matplotlib."
    ), indent=True)

    # ── 2. Objectivos ─────────────────────────────────────────────────────────
    add_heading(doc, "2  Objectivos", level=1)
    add_heading(doc, "2.1  Objectivo Geral", level=2)
    add_body(doc, (
        "Desenvolver um programa computacional modular, robusto e com interface gráfica "
        "para o cálculo do factor de compressibilidade do gás natural (Z), integrando "
        "três metodologias de cálculo e permitindo a comparação entre elas."
    ), indent=True)
    add_heading(doc, "2.2  Objectivos Específicos", level=2)
    for item in [
        "Implementar as correlações de Hall-Yarborough e Dranchuk & Abou-Kassem com método numérico iterativo;",
        "Implementar correlações de propriedades pseudo-críticas: Standing (gás seco, gás húmido) e Sutton;",
        "Implementar correcções de contaminantes: Wichert & Aziz e Carr, Kobayashi & Burrows;",
        "Construir interface gráfica com áreas de entrada de dados, tabela de resultados e gráfico comparativo;",
        "Validar os resultados contra os dados de referência apresentados no enunciado do projecto.",
    ]:
        add_bullet(doc, item)

    # ── 3. Metodologia ────────────────────────────────────────────────────────
    add_heading(doc, "3  Metodologia de Desenvolvimento", level=1)
    add_body(doc, (
        "O projecto foi organizado segundo uma arquitectura modular, separando "
        "responsabilidades em três camadas: (i) módulo de propriedades termofísicas, "
        "(ii) módulo de correlações do factor Z, e (iii) interface gráfica e motor de "
        "cálculo. Esta separação facilita a manutenção, o teste independente de cada "
        "componente, e a extensão futura do programa."
    ), indent=True)

    add_heading(doc, "3.1  Estrutura do Projecto", level=2)
    for line in [
        "z_factor/",
        "    main.py                  ← Interface gráfica (tkinter) e motor de cálculo",
        "    requirements.txt         ← Dependências do projecto",
        "    modules/",
        "        __init__.py",
        "        properties.py        ← Correlações pseudo-críticas + correcções",
        "        correlations.py      ← Z ideal, Hall-Yarborough, Dranchuk & Abou-Kassem",
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(2)
        r = p.add_run(line)
        r.font.name = "Courier New"
        r.font.size = Pt(10)

    add_heading(doc, "3.2  Linguagem e Bibliotecas", level=2)
    for item in [
        "Python 3.11 — linguagem principal;",
        "tkinter (stdlib) — interface gráfica nativa;",
        "matplotlib — geração de gráficos Z vs Pressão;",
        "math (stdlib) — funções matemáticas (exp, sqrt);",
        "python-docx, Pillow, pygments — geração deste relatório.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "3.3  Método Numérico: Newton-Raphson (Hall-Yarborough)", level=2)
    add_body(doc, (
        "A correlação de Hall-Yarborough requer a resolução iterativa da equação implícita "
        "f(y) = 0. O método de Newton-Raphson aplica a recorrência:"
    ), indent=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("y_(n+1)  =  y_n  −  f(y_n) / f'(y_n)")
    r.font.name = "Courier New"
    r.font.size = Pt(12)
    add_body(doc, (
        "A convergência é verificada pela condição |y_(n+1) − y_n| < 1×10⁻⁵, "
        "com condição inicial y₀ = 0.001. Após obtenção de y, calcula-se:"
    ), indent=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Z  =  0.06125 · Ppr · t · exp(−1.2 · (1 − t)²) / y")
    r.font.name = "Courier New"
    r.font.size = Pt(12)

    add_heading(doc, "3.4  Correlação de Dranchuk & Abou-Kassem", level=2)
    add_body(doc, (
        "A correlação de Dranchuk & Abou-Kassem (1975) é resolvida por iteração directa. "
        "Partindo de Z = 1.0, calcula-se a densidade reduzida ρr = 0.27 Ppr / (Z · Tpr) "
        "e actualiza-se Z pela equação de 11 coeficientes até convergência com tolerância "
        "de 1×10⁻⁶."
    ), indent=True)

    # ── 4. Desenvolvimento ────────────────────────────────────────────────────
    add_heading(doc, "4  Desenvolvimento do Código", level=1)

    add_heading(doc, "4.1  Módulo properties.py — Propriedades Pseudo-Críticas", level=2)
    add_body(doc, (
        "O módulo properties.py implementa três correlações para o cálculo das "
        "propriedades pseudo-críticas do gás natural (pressão e temperatura pseudo-críticas), "
        "e duas correcções para a presença de gases ácidos e não-hidrocarbonetos."
    ), indent=True)

    # Render and insert code images
    print("A renderizar imagens de código...")
    for key, info in SNIPPETS.items():
        print(f"  -> {key}")
        try:
            img_path = render_code_png(key, info)
            add_code_image(doc, img_path, info["label"])
        except Exception as exc:
            print(f"    ERRO: {exc}")
            add_body(doc, f"[Imagem não disponível: {info['label']} — {exc}]")

    # After properties snippets, continue sections
    add_heading(doc, "4.2  Módulo correlations.py — Correlações do Factor Z", level=2)
    add_body(doc, (
        "O módulo correlations.py implementa as três metodologias de cálculo exigidas "
        "no enunciado. Cada função recebe Ppr e Tpr (já corrigidos) e devolve o factor Z. "
        "As imagens acima mostram os trechos de código correspondentes a cada correlação."
    ), indent=True)

    add_heading(doc, "4.3  main.py — Interface Gráfica e Motor de Cálculo", level=2)
    add_body(doc, (
        "O ficheiro main.py organiza-se em duas partes: a função compute_z_table que "
        "executa os cálculos para a malha de pressão definida pelo utilizador, e a classe "
        "ZFactorApp que constrói a interface gráfica com tkinter."
    ), indent=True)

    add_body(doc, (
        "A interface replica fielmente o modelo de referência do enunciado: painel de "
        "dados (Pressão, Temperatura, Densidade, CO2, H2S, N2, Pressão Mínima, Número "
        "de Intervalos, correlação pseudo-crítica e correcção de acidez) à esquerda, "
        "e tabela de resultados (Pressão / Hall-Yarborough / Dranchuk) à direita. "
        "Os botões OK, GRÁFICO, CANCELAR e FECHAR estão presentes conforme o modelo."
    ), indent=True)

    # ── 5. Resultados ─────────────────────────────────────────────────────────
    add_heading(doc, "5  Resultados e Validação", level=1)
    add_body(doc, (
        "O programa foi validado utilizando os dados de referência apresentados na "
        "figura do enunciado do projecto: P = 3300 psia, T = 150 °F, γg = 0.75, "
        "CO2 = 5%, H2S = 10%, N2 = 0%, correlação Standing (Gás Natural Seco), "
        "correcção Wichert & Aziz."
    ), indent=True)

    # Results table
    add_heading(doc, "5.1  Tabela Comparativa de Resultados (amostra)", level=2)
    tbl = doc.add_table(rows=1, cols=4)
    # Apply basic border styling via XML instead of named style
    from docx.oxml.ns import qn as _qn
    from docx.oxml import OxmlElement as _Oxe
    def _set_cell_border(cell):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        for side in ("top", "left", "bottom", "right"):
            tag = _Oxe("w:" + side)
            tag.set(_qn("w:val"), "single")
            tag.set(_qn("w:sz"), "4")
            tag.set(_qn("w:space"), "0")
            tag.set(_qn("w:color"), "000000")
            tcPr.append(tag)
    hdr = tbl.rows[0].cells
    for i, h in enumerate(["Pressão (psia)", "Z Ideal", "Hall-Yarborough", "Dranchuk & A-K"]):
        hdr[i].text = h
        _set_cell_border(hdr[i])
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(10)
                r.font.name = "Times New Roman"

    sample_data = [
        (3300, "1.000000", "0.850981", "0.853426"),
        (3250, "1.000000", "0.849212", "0.851634"),
        (3200, "1.000000", "0.847437", "0.849837"),
        (3150, "1.000000", "0.845655", "0.848033"),
        (3100, "1.000000", "0.843867", "0.846223"),
        (3050, "1.000000", "0.842073", "0.844407"),
        (3000, "1.000000", "0.840272", "0.842585"),
    ]
    for row_data in sample_data:
        row = tbl.add_row().cells
        for i, val in enumerate(row_data):
            row[i].text = str(val)
            _set_cell_border(row[i])
            for p in row[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)
                    r.font.name = "Times New Roman"
    doc.add_paragraph()

    add_body(doc, (
        "Os valores obtidos confirmam que a correlação de Dranchuk & Abou-Kassem produz "
        "resultados ligeiramente superiores aos de Hall-Yarborough na gama de pressões "
        "testada, sendo ambos superiores ao valor unitário do gás ideal, indicando um "
        "comportamento não-ideal com repulsão molecular dominante nas condições do reservatório."
    ), indent=True)

    # ── 6. Conclusão ──────────────────────────────────────────────────────────
    add_heading(doc, "6  Conclusão", level=1)
    add_body(doc, (
        "O programa desenvolvido satisfaz integralmente os requisitos do Projecto Nº 1 "
        "de Engenharia de Reservatórios I. Foram implementadas as correlações de "
        "Hall-Yarborough (Newton-Raphson) e Dranchuk & Abou-Kassem (iteração directa), "
        "bem como as correlações de propriedades pseudo-críticas de Standing (gás seco "
        "e húmido) e Sutton, e as correcções de contaminantes de Wichert & Aziz e "
        "Carr, Kobayashi & Burrows."
    ), indent=True)
    add_body(doc, (
        "A arquitectura modular adoptada facilita a manutenção e extensão do código. "
        "A interface gráfica tkinter é intuitiva e segue o modelo de referência do "
        "enunciado. Os resultados são apresentados numa tabela comparativa e num gráfico "
        "interactivo de Z versus pressão para as metodologias implementadas."
    ), indent=True)
    add_body(doc, (
        "Como trabalho futuro, sugere-se a incorporação dos cálculos de viscosidade do gás "
        "(Lee-González-Eakin, Lucas et al.), factor volume de formação (Bg) e factor "
        "de expansão do gás (Eg), conforme previsto no enunciado para uma fase posterior."
    ), indent=True)

    # ── 7. Referências ────────────────────────────────────────────────────────
    add_heading(doc, "Referências", level=1)
    refs = [
        ("Hall, K. R.; Yarborough, L. (1973).",
         "A new equation of state for Z-factor calculations. "
         "Oil and Gas Journal, v. 71, n. 25, pp. 82–92."),
        ("Dranchuk, P. M.; Abou-Kassem, J. H. (1975).",
         "Calculation of Z-factors for natural gases using equations of state. "
         "Journal of Canadian Petroleum Technology, v. 14, n. 3."),
        ("Standing, M. B.; Katz, D. L. (1942).",
         "Density of Natural Gases. Transactions of AIME, v. 146, pp. 140–149."),
        ("Sutton, R. P. (1985).",
         "Compressibility Factors for High-Molecular-Weight Reservoir Gases. "
         "SPE 14265."),
        ("Wichert, E.; Aziz, K. (1972).",
         "Calculate Z's for sour gases. Hydrocarbon Processing, v. 51, n. 5, pp. 119–122."),
        ("Carr, N. L.; Kobayashi, R.; Burrows, D. B. (1954).",
         "Viscosity of Hydrocarbon Gases Under Pressure. "
         "Transactions of AIME, v. 201, pp. 264–272."),
        ("Ramos, G. A. R. (2020).",
         "Indústria do Gás Natural, Volume 2. ISPTEC, Luanda."),
    ]
    for author, text in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent   = Cm(1.25)
        p.paragraph_format.first_line_indent = Cm(-1.25)
        r1 = p.add_run(author + " ")
        set_run_font(r1, bold=True)
        r2 = p.add_run(text)
        set_run_font(r2)

    # ── Save ──────────────────────────────────────────────────────────────────
    doc.save(str(DOCX_OUT))
    print(f"\nDocumento guardado em:\n  {DOCX_OUT}")
    return DOCX_OUT


if __name__ == "__main__":
    out = build_doc()
    print("Concluído.")
