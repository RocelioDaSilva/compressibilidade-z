"""
Factor de Compressibilidade de Gás Natural (Z-Factor)
======================================================
Engenharia de Reservatórios I — 2025/2026 — Projecto Nº 1
Instituto Superior Politécnico de Tecnologias e Ciências

Docente: Geraldo Ramos, BSc, MSc, PhD

Interface gráfica com tkinter para calcular o factor Z usando:
  1. Gás Ideal (Z = 1)
  2. Correlação de Hall-Yarborough  (Newton-Raphson)
  3. Correlação de Dranchuk & Abou-Kassem  (iteração directa)
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ── Matplotlib opcional (para gráfico) ───────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ── Módulos locais ────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from modules.properties import (
    standing_seco,
    standing_humido,
    sutton,
    wichert_aziz,
    carr_kobayashi_burrows,
)
from modules.correlations import (
    z_ideal,
    z_hall_yarborough,
    z_dranchuk_abou_kassem,
)

# ── Constants ─────────────────────────────────────────────────────────────────
TITLE = "Factor de Compressibilidade de Gas (Z factor) - Por Geraldo Ramos"

PSEUDOCRIT_OPTIONS = [
    "Gás Natural Seco (Standing)",
    "Gás Natural Húmido (Standing)",
    "Gás Natural (Sutton)",
]

CORRECTION_OPTIONS = [
    "Wichert e Aziz",
    "Carr, Kobayashi e Burrows",
    "Nenhuma",
]


# ── Cálculo ───────────────────────────────────────────────────────────────────

def calcular_z_tabela(
    P_max: float, T_f: float,
    gama_g: float,
    y_co2: float, y_h2s: float, y_n2: float,
    P_min: float, n_int: int,
    pc_choice: str, corr_choice: str,
) -> list:
    """Calcular tabela do factor Z para uma grelha de pressões.

    Args:
        P_max, P_min : gama de pressão [psia]
        T_f          : temperatura [°F]
        gama_g       : densidade relativa do gás (fracção)
        y_co2/h2s/n2 : fracções molares de não-hidrocarbonetos (fracção)
        n_int        : número de intervalos de pressão
        pc_choice    : etiqueta da correlação pseudo-crítica
        corr_choice  : etiqueta da correcção de gases ácidos

    Returns:
        Lista de tuplos (pressão, z_hy, z_dak).
    """
    T_R = T_f + 459.67   # °F → °R

    # Propriedades pseudo-críticas
    if "Húmido" in pc_choice:
        Ppc, Tpc = standing_humido(gama_g)
    elif "Sutton" in pc_choice:
        Ppc, Tpc = sutton(gama_g)
    else:
        Ppc, Tpc = standing_seco(gama_g)

    # Correcção para gases ácidos / não-hidrocarbonetos
    if "Wichert" in corr_choice:
        Ppc, Tpc = wichert_aziz(Ppc, Tpc, y_co2, y_h2s)
    elif "Carr" in corr_choice:
        Ppc, Tpc = carr_kobayashi_burrows(Ppc, Tpc, y_co2, y_h2s, y_n2)

    Tpr = T_R / Tpc
    passo = (P_max - P_min) / n_int

    resultados = []
    for i in range(n_int + 1):
        P = P_max - i * passo
        Ppr = P / Ppc
        resultados.append((
            P,
            z_hall_yarborough(Ppr, Tpr),
            z_dranchuk_abou_kassem(Ppr, Tpr),
        ))

    return resultados


# ── Interface Gráfica ─────────────────────────────────────────────────────────

class AplicacaoFactorZ(tk.Tk):
    """Janela principal da aplicação."""

    def __init__(self):
        super().__init__()
        self.title(TITLE)
        self.resizable(True, True)
        self.minsize(800, 560)
        self._resultados: list = []
        self._construir_interface()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _construir_interface(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        raiz = ttk.Frame(self, padding=10)
        raiz.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        raiz.columnconfigure(1, weight=1)
        raiz.rowconfigure(0, weight=1)

        self._construir_esquerda(raiz)
        self._construir_direita(raiz)
        self._construir_botoes(raiz)

    def _construir_esquerda(self, parent):
        frame = ttk.LabelFrame(parent, text="Dados", padding=10)
        frame.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        FIELDS = [
            ("Pressão (Psia):",        "pressao",     "3300"),
            ("Temperatura (°F):",      "temperatura", "150"),
            ("Densidade (%γg):",       "densidade",   "75"),
            ("CO2 (%):",               "co2",         "5"),
            ("H2S (%):",               "h2s",         "10"),
            ("N2 (%):",                "n2",          "0"),
            ("Pressão Mínima (Psia):", "pressao_min", "3000"),
            ("Número de Intervalos:",  "n_int",       "50"),
        ]

        self.vars: dict = {}
        for r, (label, key, val) in enumerate(FIELDS):
            ttk.Label(frame, text=label, anchor="w").grid(
                row=r, column=0, sticky="w", pady=3, padx=(0, 8))
            v = tk.StringVar(value=val)
            self.vars[key] = v
            ttk.Entry(frame, textvariable=v, width=14).grid(
                row=r, column=1, sticky="ew", pady=3)

        row = len(FIELDS)
        ttk.Separator(frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=6)
        row += 1

        ttk.Label(frame, text="P e T Pseudocríticas:", anchor="w").grid(
            row=row, column=0, sticky="w", pady=3)
        self.vars["pseudocrit"] = tk.StringVar(value=PSEUDOCRIT_OPTIONS[0])
        cb1 = ttk.Combobox(
            frame, textvariable=self.vars["pseudocrit"],
            values=PSEUDOCRIT_OPTIONS, width=26, state="readonly")
        cb1.grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        ttk.Label(frame, text="Correcção de acidez:", anchor="w").grid(
            row=row, column=0, sticky="w", pady=3)
        self.vars["correcao"] = tk.StringVar(value=CORRECTION_OPTIONS[0])
        cb2 = ttk.Combobox(
            frame, textvariable=self.vars["correcao"],
            values=CORRECTION_OPTIONS, width=26, state="readonly")
        cb2.grid(row=row, column=1, sticky="ew", pady=3)

        frame.columnconfigure(1, weight=1)

    def _construir_direita(self, parent):
        frame = ttk.LabelFrame(parent, text="Resultados", padding=10)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        cols = ("Pressão", "Hall-Yarborough", "Dranchuk")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=22)
        for col, w in zip(cols, (90, 135, 135)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=70, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

    def _construir_botoes(self, parent):
        frame = ttk.Frame(parent)
        frame.grid(row=1, column=0, columnspan=2, pady=(12, 0))

        botoes = [
            ("OK",        self.calcular),
            ("GRÁFICO",   self.mostrar_grafico),
            ("CANCELAR",  self.limpar),
            ("FECHAR",    self.destroy),
        ]
        for i, (text, cmd) in enumerate(botoes):
            ttk.Button(frame, text=text, command=cmd, width=13).grid(
                row=0, column=i, padx=8)

    # ── Auxiliares ────────────────────────────────────────────────────────────

    def _float(self, key: str, label: str) -> float:
        try:
            return float(self.vars[key].get().replace(",", "."))
        except ValueError:
            raise ValueError(f"Valor inválido para «{label}»")

    # ── Acções ────────────────────────────────────────────────────────────────

    def calcular(self):
        """Ler entradas, validar, executar cálculo e preencher tabela."""
        try:
            P_max   = self._float("pressao",     "Pressão")
            T_f     = self._float("temperatura", "Temperatura")
            gama_g  = self._float("densidade",   "Densidade") / 100.0
            y_co2   = self._float("co2",         "CO2")  / 100.0
            y_h2s   = self._float("h2s",         "H2S")  / 100.0
            y_n2    = self._float("n2",          "N2")   / 100.0
            P_min   = self._float("pressao_min", "Pressão Mínima")
            n_int   = int(self._float("n_int",   "Número de Intervalos"))
        except ValueError as exc:
            messagebox.showerror("Erro de entrada", str(exc), parent=self)
            return

        if P_min >= P_max:
            messagebox.showerror(
                "Erro", "Pressão Mínima deve ser menor que Pressão Máxima.",
                parent=self)
            return
        if n_int < 1:
            messagebox.showerror(
                "Erro", "Número de Intervalos deve ser ≥ 1.", parent=self)
            return

        try:
            self._resultados = calcular_z_tabela(
                P_max, T_f, gama_g, y_co2, y_h2s, y_n2,
                P_min, n_int,
                self.vars["pseudocrit"].get(),
                self.vars["correcao"].get(),
            )
        except Exception as exc:
            messagebox.showerror("Erro de cálculo", str(exc), parent=self)
            return

        # Preencher a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        for P, z_hy, z_dak in self._resultados:
            self.tree.insert(
                "", "end",
                values=(f"{P:.1f}", f"{z_hy:.6f}", f"{z_dak:.6f}"))

    def mostrar_grafico(self):
        """Abrir nova janela com gráfico de Z vs Pressão."""
        if not self._resultados:
            messagebox.showinfo(
                "Sem dados", "Execute o cálculo primeiro (botão OK).",
                parent=self)
            return
        if not HAS_MATPLOTLIB:
            messagebox.showwarning(
                "matplotlib não encontrado",
                "Instale matplotlib:\n  pip install matplotlib",
                parent=self)
            return

        pressoes = [r[0] for r in self._resultados]
        z_hy  = [r[1] for r in self._resultados]
        z_dak = [r[2] for r in self._resultados]
        z_id  = [z_ideal()] * len(pressoes)

        win = tk.Toplevel(self)
        win.title("Factor Z vs Pressão")
        win.resizable(True, True)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(pressoes, z_id,  "g--",  lw=1.5, label="Gás Ideal (Z = 1)")
        ax.plot(pressoes, z_hy,  "b-",   lw=2.0, label="Hall-Yarborough")
        ax.plot(pressoes, z_dak, "r-.",  lw=2.0, label="Dranchuk e Abou-Kassem")
        ax.set_xlabel("Pressão (Psia)", fontsize=11)
        ax.set_ylabel("Factor Z",       fontsize=11)
        ax.set_title("Factor de Compressibilidade do Gás Natural", fontsize=13)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.35)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        ttk.Button(win, text="Fechar", command=win.destroy).pack(pady=6)

    def limpar(self):
        """Limpar tabela de resultados."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._resultados = []


# ── Ponto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AplicacaoFactorZ()
    app.mainloop()
