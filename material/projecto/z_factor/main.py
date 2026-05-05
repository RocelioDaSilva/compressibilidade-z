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

# ── Paleta de cores ISPTEC ────────────────────────────────────────────────────
C = {
    "navy":     "#1A3C5E",
    "navy_lt":  "#254F7A",
    "navy_dk":  "#122A42",
    "gold":     "#C8861E",
    "gold_lt":  "#DFA030",
    "bg":       "#EEF2F7",
    "card":     "#FFFFFF",
    "text":     "#2C3E50",
    "muted":    "#7F8C8D",
    "border":   "#C8D8E8",
    "row_alt":  "#EEF6FF",
    "green":    "#27AE60",
    "red":      "#C0392B",
    "blue":     "#2980B9",
    "purple":   "#8E44AD",
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

    Returns:
        (linhas, (Ppc, Tpc, Tpr))
        linhas: lista de (P, Z, mu [cP], Bg, Eg)
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

        # Factor Z
        if "Dranchuk" in z_ch:
            Z = z_dranchuk_abou_kassem(Ppr, Tpr)
        else:
            Z = z_hall_yarborough(Ppr, Tpr)

        # Viscosidade
        if "Lucas" in visc_ch:
            mu = viscosidade_lucas(T_R, P, Ppc, Tpc, gama_g)
        else:
            mu = viscosidade_lee_gonzalez_eakin(T_R, P, Z, gama_g)

        Bg = fn_bg(Z, T_R, P)
        Eg = fn_eg(Z, T_R, P)
        linhas.append((P, Z, mu, Bg, Eg))

    return linhas, (Ppc, Tpc, Tpr)


# ── Estilo ttk ────────────────────────────────────────────────────────────────

def _estilo(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(bg=C["bg"])

    s.configure("TFrame",      background=C["bg"])
    s.configure("Card.TFrame", background=C["card"])

    s.configure("TLabelframe",
                background=C["card"],
                foreground=C["navy"],
                bordercolor=C["border"],
                relief="groove")
    s.configure("TLabelframe.Label",
                background=C["card"],
                foreground=C["navy"],
                font=("Segoe UI", 10, "bold"))

    s.configure("TLabel",
                background=C["card"],
                foreground=C["text"],
                font=("Segoe UI", 10))
    s.configure("BG.TLabel",
                background=C["bg"],
                foreground=C["text"],
                font=("Segoe UI", 10))
    s.configure("Muted.TLabel",
                background=C["card"],
                foreground=C["muted"],
                font=("Segoe UI", 9, "italic"))

    s.configure("TEntry",
                fieldbackground="white",
                foreground=C["text"],
                bordercolor=C["border"],
                font=("Segoe UI", 10))

    s.configure("TCombobox",
                fieldbackground="white",
                foreground=C["text"],
                font=("Segoe UI", 10))

    # Botões
    for name, bg, hover in [
        ("Primary", C["navy"],  C["navy_lt"]),
        ("Gold",    C["gold"],  C["gold_lt"]),
        ("Danger",  C["red"],   "#E74C3C"),
        ("Outline", C["bg"],    C["border"]),
    ]:
        s.configure(f"{name}.TButton",
                    background=bg,
                    foreground="white" if name != "Outline" else C["navy"],
                    font=("Segoe UI", 10, "bold"),
                    padding=(14, 8),
                    relief="flat",
                    borderwidth=0)
        s.map(f"{name}.TButton",
              background=[("active", hover), ("pressed", bg)])

    # Treeview
    s.configure("Treeview",
                background=C["card"],
                foreground=C["text"],
                fieldbackground=C["card"],
                rowheight=28,
                font=("Consolas", 10),
                bordercolor=C["border"])
    s.configure("Treeview.Heading",
                background=C["navy"],
                foreground="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                padding=(6, 5))
    s.map("Treeview",
          background=[("selected", C["navy_lt"])],
          foreground=[("selected", "white")])
    s.map("Treeview.Heading",
          background=[("active", C["navy_lt"])])


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
        hdr = tk.Frame(self, bg=C["navy"], padx=18, pady=13)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(1, weight=1)

        # Ícone circular
        cnv = tk.Canvas(hdr, width=50, height=50,
                        bg=C["navy"], highlightthickness=0)
        cnv.grid(row=0, column=0, rowspan=2, padx=(0, 16))
        cnv.create_oval(2, 2, 48, 48, fill=C["gold"], outline="")
        cnv.create_text(25, 25, text="Z", fill="white",
                        font=("Segoe UI", 22, "bold"))

        tk.Label(hdr,
                 text="Factor de Compressibilidade do Gás Natural",
                 bg=C["navy"], fg="white",
                 font=("Segoe UI", 15, "bold")).grid(
                 row=0, column=1, sticky="w")
        tk.Label(hdr,
                 text=("Engenharia de Reservatórios I — 2025/2026  |  "
                       "ISPTEC  |  Docente: Geraldo Ramos, BSc, MSc, PhD"),
                 bg=C["navy"], fg=C["gold"],
                 font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w")

        # Linha dourada decorativa
        tk.Frame(self, bg=C["gold"], height=3).grid(
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

        self._cols = ("Pressão\n(Psia)", "Factor Z",
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

    def _hdrs(self):
        bg_u = self.v.get("unid_bg", tk.StringVar(value=OPT_BG[0])).get()
        eg_u = self.v.get("unid_eg", tk.StringVar(value=OPT_EG[0])).get()
        hdrs  = ["Pressão (Psia)", "Factor Z",
                 "Viscosidade (cP)",
                 f"Bg  ({bg_u})", f"Eg  ({eg_u})"]
        widths = [100, 110, 120, 130, 130]
        for col, hdr, w in zip(self._cols, hdrs, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w, minwidth=70, anchor="center")

    def _status_bar(self):
        bar = tk.Frame(self, bg=C["navy_dk"], padx=12, pady=4)
        bar.grid(row=2, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)
        self._sv = tk.StringVar(value="Pronto.")
        tk.Label(bar, textvariable=self._sv,
                 bg=C["navy_dk"], fg="white",
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        tk.Label(bar,
                 text="ISPTEC — Engenharia de Reservatórios I — v2.0",
                 bg=C["navy_dk"], fg=C["gold"],
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
        for i, (P, Z, mu, Bg, Eg) in enumerate(self._resultados):
            tag = "alt" if i % 2 else ""
            self.tree.insert("", "end", tags=(tag,),
                values=(f"{P:.1f}", f"{Z:.6f}",
                        f"{mu:.6f}", f"{Bg:.6f}", f"{Eg:.4f}"))

        n = len(self._resultados)
        self._lbl_info.config(
            text=(f"  {n} pontos  \u2502  "
                  f"Ppc = {self._Ppc:.1f} psia  \u2502  "
                  f"Tpc = {self._Tpc:.1f} \u00b0R  \u2502  "
                  f"Tpr = {self._Tpr:.3f}"),
            foreground=C["navy"])
        self._sv.set(f"Cálculo concluído — {n} pontos calculados com sucesso.")

    def grafico(self):
        if not self._resultados:
            messagebox.showinfo("Sem Dados",
                "Execute o cálculo primeiro (\u25b6 CALCULAR).", parent=self)
            return
        if not HAS_MPL:
            messagebox.showwarning("matplotlib em falta",
                "pip install matplotlib", parent=self); return

        P   = [r[0] for r in self._resultados]
        Zv  = [r[1] for r in self._resultados]
        mu  = [r[2] for r in self._resultados]
        Bg  = [r[3] for r in self._resultados]
        Eg  = [r[4] for r in self._resultados]

        # Z comparativo (o outro método)
        z_ch2 = (OPT_Z[1] if "Hall" in self.v["metodo_z"].get() else OPT_Z[0])
        # recalcular pseudo-críticas para o gráfico
        try:
            T_R   = self._flt("temperatura", "") + 459.67
            Tpr2  = T_R / self._Tpc
            Z2 = []
            for p_val, Zval in zip(P, Zv):
                Ppr2 = p_val / self._Ppc
                if "Dranchuk" in z_ch2:
                    Z2.append(z_dranchuk_abou_kassem(Ppr2, Tpr2))
                else:
                    Z2.append(z_hall_yarborough(Ppr2, Tpr2))
        except Exception:
            Z2 = None

        bg_u = self.v["unid_bg"].get()
        eg_u = self.v["unid_eg"].get()
        zm   = self.v["metodo_z"].get()
        vm   = self.v["metodo_visc"].get()

        win = tk.Toplevel(self)
        win.title("Gráficos — Factor Z, Viscosidade, Bg e Eg vs Pressão")
        win.configure(bg=C["bg"])
        win.resizable(True, True)

        tk.Frame(win, bg=C["navy"], padx=14, pady=8).pack(fill="x")
        tk.Label(win.winfo_children()[-1],
                 text="Propriedades do Gás Natural vs Pressão",
                 bg=C["navy"], fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left")

        fig, axes = plt.subplots(2, 2, figsize=(13, 8))
        fig.patch.set_facecolor("#F0F4F8")
        fig.suptitle("Gás Natural — Resultados Completos",
                     fontsize=14, fontweight="bold",
                     color=C["navy"], y=0.98)

        lw = dict(linewidth=2.2)
        gk = dict(alpha=0.3, linestyle="--", color="#999")

        # ── Z-factor ──────────────────────────────────────────────────
        ax = axes[0, 0]
        ax.plot(P, Zv, color=C["blue"], label=zm, **lw)
        if Z2:
            ax.plot(P, Z2, color=C["purple"],
                    linestyle="-.", linewidth=1.8, label=z_ch2)
        ax.plot(P, [z_ideal()] * len(P), color=C["green"],
                linewidth=1.5, linestyle=":", label="Gás Ideal (Z=1)")
        ax.set_xlabel("Pressão (Psia)", fontsize=10)
        ax.set_ylabel("Factor Z", fontsize=10)
        ax.set_title("Factor de Compressibilidade (Z)",
                     fontsize=11, fontweight="bold", color=C["navy"])
        ax.legend(fontsize=9)
        ax.grid(True, **gk); ax.set_facecolor("#FAFCFF")

        # ── Viscosidade ───────────────────────────────────────────────
        ax = axes[0, 1]
        ax.plot(P, mu, color=C["gold"], **lw, label=vm)
        ax.set_xlabel("Pressão (Psia)", fontsize=10)
        ax.set_ylabel("Viscosidade (cP)", fontsize=10)
        ax.set_title("Viscosidade do Gás (\u03bcg)",
                     fontsize=11, fontweight="bold", color=C["navy"])
        ax.legend(fontsize=9)
        ax.grid(True, **gk); ax.set_facecolor("#FAFCFF")

        # ── Bg ────────────────────────────────────────────────────────
        ax = axes[1, 0]
        ax.plot(P, Bg, color=C["red"], **lw)
        ax.set_xlabel("Pressão (Psia)", fontsize=10)
        ax.set_ylabel(f"Bg  ({bg_u})", fontsize=10)
        ax.set_title("Factor Volume de Formação (Bg)",
                     fontsize=11, fontweight="bold", color=C["navy"])
        ax.grid(True, **gk); ax.set_facecolor("#FAFCFF")

        # ── Eg ────────────────────────────────────────────────────────
        ax = axes[1, 1]
        ax.plot(P, Eg, color=C["purple"], **lw)
        ax.set_xlabel("Pressão (Psia)", fontsize=10)
        ax.set_ylabel(f"Eg  ({eg_u})", fontsize=10)
        ax.set_title("Factor de Expansão do Gás (Eg)",
                     fontsize=11, fontweight="bold", color=C["navy"])
        ax.grid(True, **gk); ax.set_facecolor("#FAFCFF")

        fig.tight_layout(rect=[0, 0, 1, 0.96])

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, win)
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
            foreground=C["muted"])
        self._sv.set("Pronto.")


# ── Ponto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AplicacaoFactorZ()
    app.mainloop()
