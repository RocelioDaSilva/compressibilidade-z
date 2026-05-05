"""
Factor de Compressibilidade de Gás Natural — Aplicação Completa
================================================================
Engenharia de Reservatórios I — 2025/2026 — Projecto Nº 1
ISPTEC — Instituto Superior Politécnico de Tecnologias e Ciências

Docente: Geraldo Ramos, BSc, MSc, PhD

Funcionalidades:
  • Factor Z      : Gás Ideal | Hall-Yarborough | Dranchuk e Abou-Kassem
  • Viscosidade   : Lee, González e Eakin | Lucas et al.
  • Bg (Fac. Vol. de Formação) : ft³/scf | bbl/Mscf | m³/m³
  • Eg (Fac. Expansão)         : scf/ft³ | Mscf/bbl | m³/m³
  • Propriedades pseudo-críticas : Standing (seco/húmido) | Sutton
  • Correcções de acidez         : Wichert e Aziz | Carr-KB
"""

import sys, os
import tkinter as tk
from tkinter import ttk, messagebox

# ── matplotlib opcional ───────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg, NavigationToolbar2Tk)
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ── módulos locais ────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from modules.properties   import (standing_seco, standing_humido, sutton,
                                   wichert_aziz, carr_kobayashi_burrows)
from modules.correlations import (z_ideal, z_hall_yarborough,
                                   z_dranchuk_abou_kassem)
from modules.viscosidade  import (viscosidade_lee_gonzalez_eakin,
                                   viscosidade_lucas)
from modules.volumetria   import (bg_ft3_scf, bg_bbl_Mscf, bg_m3_m3,
                                   eg_scf_ft3, eg_Mscf_bbl, eg_m3_m3)

# ── Paleta de cores — tema escuro moderno ─────────────────────────────────────
C = {
    # estrutura
    "bg":         "#0e1621",   # fundo principal
    "panel":      "#152131",   # painéis / cards
    "panel2":     "#1a2940",   # painéis secundários
    "border":     "#1e3a5f",   # bordas
    # acentos
    "accent":     "#00b4d8",   # ciano petróleo (cor primária)
    "accent2":    "#00c896",   # verde-ciano (2.ª cor)
    "gold":       "#d4930a",   # âmbar ISPTEC
    "gold_lt":    "#f0b020",   # âmbar claro (hover)
    # texto
    "text":       "#cce5f5",   # texto principal
    "muted":      "#4d7a9a",   # texto secundário
    "text_head":  "#ffffff",   # cabeçalhos
    # campos de entrada
    "entry_bg":   "#0a1826",
    "entry_fg":   "#b8d8ee",
    # tabela
    "table_bg":   "#0d1d2e",
    "row_alt":    "#132438",
    "table_head": "#0b2444",
    "sel":        "#004080",
    # botões
    "btn_ok":     "#005f38",
    "btn_ok_h":   "#007a4a",
    "btn_gold":   "#6b4400",
    "btn_gold_h": "#7a5200",
    "btn_out":    "#1e3a5f",
    "btn_out_h":  "#2a4f7a",
    "btn_danger": "#6b1c1c",
    "btn_dng_h":  "#8b2424",
    # gráficos
    "green":      "#00b894",
    "red":        "#e74c3c",
    "blue":       "#0984e3",
    "purple":     "#a29bfe",
    # aliases para manter compatibilidade
    "navy":       "#152131",
    "navy_lt":    "#1a2940",
    "navy_dk":    "#0e1621",
    "card":       "#152131",
}

# ── Opções de correlações ────────────────────────────────────────────────────
OPT_PC   = ["Gás Natural Seco (Standing)",
             "Gás Natural Húmido (Standing)",
             "Gás Natural (Sutton)"]
OPT_CORR = ["Wichert e Aziz", "Carr, Kobayashi e Burrows", "Nenhuma"]
OPT_Z    = ["Hall-Yarborough", "Dranchuk e Abou-Kassem"]
OPT_VISC = ["Lee, González e Eakin", "Lucas et al."]
OPT_BG   = ["ft\u00b3/scf", "bbl/Mscf", "m\u00b3/m\u00b3"]
OPT_EG   = ["scf/ft\u00b3", "Mscf/bbl", "m\u00b3/m\u00b3"]

_BG_FN = {"ft\u00b3/scf": bg_ft3_scf,
           "bbl/Mscf":   bg_bbl_Mscf,
           "m\u00b3/m\u00b3":  bg_m3_m3}
_EG_FN = {"scf/ft\u00b3": eg_scf_ft3,
           "Mscf/bbl":    eg_Mscf_bbl,
           "m\u00b3/m\u00b3":  eg_m3_m3}

TITULO = ("Factor de Compressibilidade do Gás Natural (Z) "
          "— Viscosidade, Bg e Eg — Por Geraldo Ramos")


# ── Motor de cálculo ─────────────────────────────────────────────────────────

def calcular_resultados(
    P_max, T_f, gama_g,
    y_co2, y_h2s, y_n2,
    P_min, n_int,
    pc_ch, corr_ch, z_ch, visc_ch, bg_ch, eg_ch,
):
    """
    Calcular tabela de resultados para a grelha de pressões escolhida.

    Calcula SEMPRE os dois métodos Z (Hall-Yarborough e Dranchuk-Abou-Kassem)
    para comparação directa. O método seleccionado em z_ch é utilizado para
    o cálculo de viscosidade, Bg e Eg.

    Returns:
        (linhas, (Ppc, Tpc, Tpr))
        linhas: lista de (P, Z_hy, Z_dak, mu [cP], Bg, Eg)
    """
    T_R = T_f + 459.67

    # Propriedades pseudo-críticas
    if "Húmido" in pc_ch:
        Ppc, Tpc = standing_humido(gama_g)
    elif "Sutton" in pc_ch:
        Ppc, Tpc = sutton(gama_g)
    else:
        Ppc, Tpc = standing_seco(gama_g)

    # Correcção de acidez
    if "Wichert" in corr_ch:
        Ppc, Tpc = wichert_aziz(Ppc, Tpc, y_co2, y_h2s)
    elif "Carr" in corr_ch:
        Ppc, Tpc = carr_kobayashi_burrows(Ppc, Tpc, y_co2, y_h2s, y_n2)

    Tpr   = T_R / Tpc
    passo = (P_max - P_min) / n_int
    fn_bg = _BG_FN[bg_ch]
    fn_eg = _EG_FN[eg_ch]

    linhas = []
    for i in range(n_int + 1):
        P   = P_max - i * passo
        Ppr = P / Ppc

        # Calcular AMBOS os métodos Z sempre
        Z_hy  = z_hall_yarborough(Ppr, Tpr)
        Z_dak = z_dranchuk_abou_kassem(Ppr, Tpr)

        # Usar o método seleccionado para viscosidade/Bg/Eg
        Z = Z_dak if "Dranchuk" in z_ch else Z_hy

        # Viscosidade
        if "Lucas" in visc_ch:
            mu = viscosidade_lucas(T_R, P, Ppc, Tpc, gama_g)
        else:
            mu = viscosidade_lee_gonzalez_eakin(T_R, P, Z, gama_g)

        Bg = fn_bg(Z, T_R, P)
        Eg = fn_eg(Z, T_R, P)
        linhas.append((P, Z_hy, Z_dak, mu, Bg, Eg))

    return linhas, (Ppc, Tpc, Tpr)


# ── Estilo ttk ────────────────────────────────────────────────────────────────

def _estilo(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(bg=C["bg"])

    s.configure("TFrame",      background=C["bg"])
    s.configure("Card.TFrame", background=C["panel"])

    # LabelFrame
    s.configure("TLabelframe",
                background=C["panel"],
                foreground=C["accent"],
                bordercolor=C["border"],
                relief="flat",
                borderwidth=1)
    s.configure("TLabelframe.Label",
                background=C["panel"],
                foreground=C["accent"],
                font=("Segoe UI", 10, "bold"),
                padding=(4, 0))

    # Labels
    s.configure("TLabel",
                background=C["panel"],
                foreground=C["text"],
                font=("Segoe UI", 10))
    s.configure("BG.TLabel",
                background=C["bg"],
                foreground=C["text"],
                font=("Segoe UI", 10))
    s.configure("Muted.TLabel",
                background=C["panel"],
                foreground=C["muted"],
                font=("Segoe UI", 9, "italic"))

    # Entry
    s.configure("TEntry",
                fieldbackground=C["entry_bg"],
                foreground=C["entry_fg"],
                insertcolor=C["accent"],
                bordercolor=C["border"],
                lightcolor=C["border"],
                darkcolor=C["border"],
                font=("Segoe UI", 10))
    s.map("TEntry",
          fieldbackground=[("focus", "#0f2438")],
          bordercolor=[("focus", C["accent"])])

    # Combobox
    s.configure("TCombobox",
                fieldbackground=C["entry_bg"],
                background=C["panel2"],
                foreground=C["entry_fg"],
                arrowcolor=C["accent"],
                selectbackground=C["sel"],
                selectforeground=C["text_head"],
                bordercolor=C["border"],
                font=("Segoe UI", 10))
    s.map("TCombobox",
          fieldbackground=[("readonly", C["entry_bg"])],
          foreground=[("readonly", C["entry_fg"])],
          selectbackground=[("readonly", C["sel"])])

    # Scrollbar
    s.configure("Vertical.TScrollbar",
                background=C["panel2"],
                troughcolor=C["table_bg"],
                arrowcolor=C["accent"],
                bordercolor=C["border"],
                darkcolor=C["panel2"],
                lightcolor=C["panel2"])
    s.configure("Horizontal.TScrollbar",
                background=C["panel2"],
                troughcolor=C["table_bg"],
                arrowcolor=C["accent"],
                bordercolor=C["border"],
                darkcolor=C["panel2"],
                lightcolor=C["panel2"])

    # Botões
    for name, bg, hover, fg in [
        ("Primary", C["btn_ok"],     C["btn_ok_h"],  "white"),
        ("Gold",    C["btn_gold"],   C["btn_gold_h"],"white"),
        ("Danger",  C["btn_danger"], C["btn_dng_h"], "white"),
        ("Outline", C["btn_out"],    C["btn_out_h"], C["text"]),
    ]:
        s.configure(f"{name}.TButton",
                    background=bg,
                    foreground=fg,
                    font=("Segoe UI", 10, "bold"),
                    padding=(14, 8),
                    relief="flat",
                    borderwidth=0,
                    focuscolor=C["border"])
        s.map(f"{name}.TButton",
              background=[("active", hover), ("pressed", bg)],
              foreground=[("active", "white")])

    # Treeview
    s.configure("Treeview",
                background=C["table_bg"],
                foreground=C["text"],
                fieldbackground=C["table_bg"],
                rowheight=26,
                font=("Consolas", 9),
                bordercolor=C["border"])
    s.configure("Treeview.Heading",
                background=C["table_head"],
                foreground=C["accent"],
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padding=(6, 5))
    s.map("Treeview",
          background=[("selected", C["sel"])],
          foreground=[("selected", C["text_head"])])
    s.map("Treeview.Heading",
          background=[("active", C["border"])])


# ── Aplicação ────────────────────────────────────────────────────────────────

class AplicacaoFactorZ(tk.Tk):
    """Aplicação principal — Factor Z, Viscosidade, Bg e Eg."""

    def __init__(self):
        super().__init__()
        self.title(TITULO)
        self.resizable(True, True)
        self.minsize(1020, 680)
        self._resultados: list = []
        self._Ppc = self._Tpc = self._Tpr = 0.0
        _estilo(self)
        self._ui()
        self.after(80, self._centrar)

    def _centrar(self):
        self.update_idletasks()
        w = max(self.winfo_reqwidth(),  1020)
        h = max(self.winfo_reqheight(), 680)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Construção ────────────────────────────────────────────────────────────

    def _ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._cabecalho()
        self._corpo()
        self._status_bar()

    def _cabecalho(self):
        hdr = tk.Frame(self, bg=C["panel"], padx=18, pady=12)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(1, weight=1)

        # Barra lateral de acento
        tk.Frame(hdr, bg=C["accent"], width=4).grid(
            row=0, column=0, rowspan=2, sticky="ns", padx=(0, 14))

        # Ícone circular com letra Z
        cnv = tk.Canvas(hdr, width=48, height=48,
                        bg=C["panel"], highlightthickness=0)
        cnv.grid(row=0, column=1, rowspan=2, padx=(0, 14))
        cnv.create_oval(1, 1, 47, 47, fill=C["accent"], outline="")
        cnv.create_text(24, 24, text="Z", fill=C["bg"],
                        font=("Segoe UI", 20, "bold"))

        tk.Label(hdr,
                 text="Factor de Compressibilidade do Gás Natural",
                 bg=C["panel"], fg=C["text_head"],
                 font=("Segoe UI", 15, "bold")).grid(
                 row=0, column=2, sticky="w")
        tk.Label(hdr,
                 text=("Engenharia de Reservatórios I — 2025/2026  |  "
                       "ISPTEC  |  Docente: Geraldo Ramos, BSc, MSc, PhD"),
                 bg=C["panel"], fg=C["gold"],
                 font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w")

        # Separador colorido
        tk.Frame(self, bg=C["accent"], height=2).grid(
            row=0, column=0, sticky="sew")

    def _corpo(self):
        f = ttk.Frame(self)
        f.grid(row=1, column=0, sticky="nsew", padx=12, pady=10)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(0, weight=1)
        self._esquerda(f)
        self._direita(f)

    def _esquerda(self, parent):
        outer = ttk.Frame(parent)
        outer.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # ── Condições ─────────────────────────────────────────────────
        fc = ttk.LabelFrame(outer, text=" Condições do Reservatório ",
                            padding=(12, 8))
        fc.pack(fill="x", pady=(0, 8))

        self.v: dict = {}
        campos = [
            ("Pressão (Psia):",         "pressao",     "3300"),
            ("Temperatura (°F):",       "temperatura", "150"),
            ("Densidade (%\u03b3g):",   "densidade",   "75"),
            ("CO\u2082 (%):",           "co2",         "5"),
            ("H\u2082S (%):",           "h2s",         "10"),
            ("N\u2082 (%):",            "n2",          "0"),
            ("Pressão Mínima (Psia):",  "pressao_min", "3000"),
            ("Nº de Intervalos:",       "n_int",       "50"),
        ]
        for r, (lbl, key, val) in enumerate(campos):
            ttk.Label(fc, text=lbl, anchor="w").grid(
                row=r, column=0, sticky="w", pady=2, padx=(0, 8))
            sv = tk.StringVar(value=val)
            self.v[key] = sv
            ttk.Entry(fc, textvariable=sv, width=13).grid(
                row=r, column=1, sticky="ew", pady=2)
        fc.columnconfigure(1, weight=1)

        # ── Correlações ───────────────────────────────────────────────
        fr = ttk.LabelFrame(outer, text=" Correlações e Métodos ",
                            padding=(12, 8))
        fr.pack(fill="x", pady=(0, 8))

        opcoes = [
            ("P,T Pseudo-críticas:",      "pseudocrit",  OPT_PC,   0),
            ("Correcção de Acidez:",      "correcao",    OPT_CORR, 0),
            ("Factor Z (método):",        "metodo_z",    OPT_Z,    0),
            ("Viscosidade do Gás:",       "metodo_visc", OPT_VISC, 0),
            ("Bg \u2014 Unidades:",       "unid_bg",     OPT_BG,   0),
            ("Eg \u2014 Unidades:",       "unid_eg",     OPT_EG,   0),
        ]
        for r, (lbl, key, opts, idx) in enumerate(opcoes):
            ttk.Label(fr, text=lbl, anchor="w").grid(
                row=r, column=0, sticky="w", pady=3, padx=(0, 8))
            sv = tk.StringVar(value=opts[idx])
            self.v[key] = sv
            ttk.Combobox(fr, textvariable=sv,
                         values=opts, width=24,
                         state="readonly").grid(
                row=r, column=1, sticky="ew", pady=3)
        fr.columnconfigure(1, weight=1)

        # ── Botões ────────────────────────────────────────────────────
        fb = ttk.Frame(outer, style="BG.TLabel")
        fb.pack(fill="x", pady=(4, 0))
        btns = [
            ("\u25b6  CALCULAR",  self.calcular,       "Primary.TButton", 0, 0),
            ("\U0001f4c8  GRÁFICO", self.grafico,      "Gold.TButton",    0, 1),
            ("\u2715  LIMPAR",    self.limpar,          "Outline.TButton", 1, 0),
            ("\u2715  FECHAR",    self.destroy,         "Danger.TButton",  1, 1),
        ]
        for txt, cmd, st, row, col in btns:
            ttk.Button(fb, text=txt, command=cmd,
                       style=st).grid(row=row, column=col,
                                      padx=4, pady=3, sticky="ew")
        fb.columnconfigure(0, weight=1)
        fb.columnconfigure(1, weight=1)

    def _direita(self, parent):
        fr = ttk.LabelFrame(parent, text=" Resultados ", padding=(8, 6))
        fr.grid(row=0, column=1, sticky="nsew")
        fr.columnconfigure(0, weight=1)
        fr.rowconfigure(1, weight=1)

        self._lbl_info = ttk.Label(
            fr,
            text="Preencha os dados e pressione  \u25b6 CALCULAR",
            style="Muted.TLabel")
        self._lbl_info.grid(row=0, column=0, columnspan=2,
                             sticky="w", pady=(0, 6), padx=4)

        self._cols = ("Pressão\n(Psia)", "Gás Ideal\n(Z=1)",
                      "Hall-Yarborough", "Dranchuk",
                      "Viscosidade\n(cP)", "Bg", "Eg")
        self.tree = ttk.Treeview(fr, columns=self._cols,
                                  show="headings", height=26)
        self._hdrs()

        vsb = ttk.Scrollbar(fr, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(fr, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

        self.tree.tag_configure("alt", background=C["row_alt"])
        self.tree.tag_configure("",    background=C["table_bg"])

    def _hdrs(self):
        bg_u = self.v.get("unid_bg", tk.StringVar(value=OPT_BG[0])).get()
        eg_u = self.v.get("unid_eg", tk.StringVar(value=OPT_EG[0])).get()
        hdrs  = ["Pressão (Psia)", "Gás Ideal (Z=1)", "Hall-Yarborough", "Dranchuk",
                 "Viscosidade (cP)", f"Bg  ({bg_u})", f"Eg  ({eg_u})"]
        widths = [95, 100, 115, 115, 120, 120, 120]
        for col, hdr, w in zip(self._cols, hdrs, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w, minwidth=70, anchor="center")

    def _status_bar(self):
        bar = tk.Frame(self, bg=C["panel"], padx=12, pady=5,
                       highlightthickness=1,
                       highlightbackground=C["border"])
        bar.grid(row=2, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)
        self._sv = tk.StringVar(value="Pronto.")
        tk.Label(bar, textvariable=self._sv,
                 bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        tk.Label(bar,
                 text="ISPTEC — Engenharia de Reservatórios I — v2.0",
                 bg=C["panel"], fg=C["gold"],
                 font=("Segoe UI", 9)).grid(row=0, column=1, sticky="e")

    # ── Auxiliar ──────────────────────────────────────────────────────────────

    def _flt(self, key, lbl):
        try:
            return float(self.v[key].get().replace(",", "."))
        except ValueError:
            raise ValueError(f"Valor inválido para «{lbl}»")

    # ── Acções ────────────────────────────────────────────────────────────────

    def calcular(self):
        try:
            P_max  = self._flt("pressao",     "Pressão")
            T_f    = self._flt("temperatura", "Temperatura")
            gama_g = self._flt("densidade",   "Densidade") / 100.0
            y_co2  = self._flt("co2",         "CO\u2082") / 100.0
            y_h2s  = self._flt("h2s",         "H\u2082S") / 100.0
            y_n2   = self._flt("n2",          "N\u2082")  / 100.0
            P_min  = self._flt("pressao_min", "Pressão Mínima")
            n_int  = int(self._flt("n_int",   "Nº de Intervalos"))
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", str(e), parent=self)
            return

        if P_min >= P_max:
            messagebox.showerror("Erro",
                "Pressão Mínima deve ser menor que Pressão Máxima.", parent=self)
            return
        if n_int < 1:
            messagebox.showerror("Erro",
                "Nº de Intervalos deve ser \u2265 1.", parent=self)
            return

        self._sv.set("A calcular…"); self.update_idletasks()

        try:
            self._resultados, (self._Ppc, self._Tpc, self._Tpr) = \
                calcular_resultados(
                    P_max, T_f, gama_g, y_co2, y_h2s, y_n2, P_min, n_int,
                    self.v["pseudocrit"].get(),
                    self.v["correcao"].get(),
                    self.v["metodo_z"].get(),
                    self.v["metodo_visc"].get(),
                    self.v["unid_bg"].get(),
                    self.v["unid_eg"].get(),
                )
        except Exception as e:
            messagebox.showerror("Erro de Cálculo", str(e), parent=self)
            self._sv.set("Erro no cálculo."); return

        self._hdrs()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (P, Z_hy, Z_dak, mu, Bg, Eg) in enumerate(self._resultados):
            tag = "alt" if i % 2 else ""
            self.tree.insert("", "end", tags=(tag,),
                values=(f"{P:.1f}", "1.000000",
                        f"{Z_hy:.6f}", f"{Z_dak:.6f}",
                        f"{mu:.6f}", f"{Bg:.6f}", f"{Eg:.4f}"))

        n = len(self._resultados)
        self._lbl_info.config(
            text=(f"  {n} pontos  \u2502  "
                  f"Ppc = {self._Ppc:.1f} psia  \u2502  "
                  f"Tpc = {self._Tpc:.1f} \u00b0R  \u2502  "
                  f"Tpr = {self._Tpr:.3f}"),
            foreground=C["accent"])
        self._sv.set(f"Cálculo concluído — {n} pontos calculados com sucesso.")

    def grafico(self):
        if not self._resultados:
            messagebox.showinfo("Sem Dados",
                "Execute o cálculo primeiro (\u25b6 CALCULAR).", parent=self)
            return
        if not HAS_MPL:
            messagebox.showwarning("matplotlib em falta",
                "pip install matplotlib", parent=self); return

        P    = [r[0] for r in self._resultados]
        Z_hy = [r[1] for r in self._resultados]
        Z_dk = [r[2] for r in self._resultados]
        mu   = [r[3] for r in self._resultados]
        Bg   = [r[4] for r in self._resultados]
        Eg   = [r[5] for r in self._resultados]

        # Usar os dois Z já calculados (não precisa recalcular)
        Zv = Z_hy if "Hall" in self.v["metodo_z"].get() else Z_dk
        z_ch2 = OPT_Z[1] if "Hall" in self.v["metodo_z"].get() else OPT_Z[0]
        Z2 = Z_dk if "Hall" in self.v["metodo_z"].get() else Z_hy

        bg_u = self.v["unid_bg"].get()
        eg_u = self.v["unid_eg"].get()
        zm   = self.v["metodo_z"].get()
        vm   = self.v["metodo_visc"].get()

        win = tk.Toplevel(self)
        win.title("Gráficos — Factor Z, Viscosidade, Bg e Eg vs Pressão")
        win.configure(bg=C["bg"])
        win.resizable(True, True)

        hdr_bar = tk.Frame(win, bg=C["panel"], padx=14, pady=8)
        hdr_bar.pack(fill="x")
        tk.Label(hdr_bar,
                 text="Propriedades do Gás Natural vs Pressão",
                 bg=C["panel"], fg=C["text_head"],
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(hdr_bar,
                 text=f"  Z: {zm}  |  μ: {vm}",
                 bg=C["panel"], fg=C["gold"],
                 font=("Segoe UI", 9)).pack(side="right")

        DARK_BG   = "#0e1621"
        DARK_AXES = "#152131"
        GRID_COL  = "#1e3a5f"
        TEXT_COL  = "#cce5f5"
        HEAD_COL  = "#ffffff"

        fig, axes = plt.subplots(2, 2, figsize=(13, 8))
        fig.patch.set_facecolor(DARK_BG)
        fig.suptitle("Gás Natural — Resultados Completos",
                     fontsize=14, fontweight="bold",
                     color=HEAD_COL, y=0.98)

        lw = dict(linewidth=2.2)
        gk = dict(alpha=0.35, linestyle="--", color=GRID_COL)

        def _dark_ax(ax, xlabel, ylabel, title):
            ax.set_facecolor(DARK_AXES)
            for spine in ax.spines.values():
                spine.set_color(GRID_COL)
            ax.tick_params(colors=TEXT_COL, labelsize=9)
            ax.xaxis.label.set_color(TEXT_COL)
            ax.yaxis.label.set_color(TEXT_COL)
            ax.set_xlabel(xlabel, fontsize=10)
            ax.set_ylabel(ylabel, fontsize=10)
            ax.set_title(title, fontsize=11, fontweight="bold", color=HEAD_COL)
            ax.grid(True, **gk)

        # ── Z-factor ──────────────────────────────────────────────────
        ax = axes[0, 0]
        ax.plot(P, Zv, color=C["accent"], label=zm, **lw)
        if Z2 is not None:
            ax.plot(P, Z2, color=C["purple"],
                    linestyle="-.", linewidth=1.8, label=z_ch2)
        ax.plot(P, [z_ideal()] * len(P), color=C["green"],
                linewidth=1.5, linestyle=":", label="Gás Ideal (Z=1)")
        leg = ax.legend(fontsize=9, facecolor=C["panel2"],
                        edgecolor=GRID_COL, labelcolor=TEXT_COL)
        _dark_ax(ax, "Pressão (Psia)", "Factor Z",
                 "Factor de Compressibilidade (Z)")

        # ── Viscosidade ───────────────────────────────────────────────
        ax = axes[0, 1]
        ax.plot(P, mu, color=C["gold_lt"], **lw, label=vm)
        ax.legend(fontsize=9, facecolor=C["panel2"],
                  edgecolor=GRID_COL, labelcolor=TEXT_COL)
        _dark_ax(ax, "Pressão (Psia)", "Viscosidade (cP)",
                 "Viscosidade do Gás (μg)")

        # ── Bg ────────────────────────────────────────────────────────
        ax = axes[1, 0]
        ax.plot(P, Bg, color=C["red"], **lw)
        _dark_ax(ax, "Pressão (Psia)", f"Bg  ({bg_u})",
                 "Factor Volume de Formação (Bg)")

        # ── Eg ────────────────────────────────────────────────────────
        ax = axes[1, 1]
        ax.plot(P, Eg, color=C["accent2"], **lw)
        _dark_ax(ax, "Pressão (Psia)", f"Eg  ({eg_u})",
                 "Factor de Expansão do Gás (Eg)")

        fig.tight_layout(rect=[0, 0, 1, 0.96])

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, win)
        toolbar.config(background=C["panel"])
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(win, text="  Fechar  ", command=win.destroy,
                   style="Danger.TButton").pack(pady=6)

    def limpar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._resultados = []
        self._lbl_info.config(
            text="Preencha os dados e pressione  \u25b6 CALCULAR",
            foreground=C["muted"],
            background=C["panel"])
        self._sv.set("Pronto.")


# ── Ponto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AplicacaoFactorZ()
    app.mainloop()
