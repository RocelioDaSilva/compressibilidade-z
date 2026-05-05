"""
Correlações de propriedades pseudo-críticas e correcções para gases ácidos.

Correlações implementadas:
  - Standing (1977): Gás Natural Seco
  - Standing (1977): Gás Natural Húmido / Condensado
  - Sutton:          Gás Natural

Correcções para gases ácidos / não-hidrocarbonetos:
  - Wichert e Aziz
  - Carr, Kobayashi e Burrows
"""

import math


# ── Propriedades pseudo-críticas ───────────────────────────────────────────────

def standing_seco(gama_g: float):
    """Standing (1977) – Gás Natural Seco.

    Args:
        gama_g: Densidade relativa do gás (ar = 1)
    Returns:
        (Ppc [psia], Tpc [°R])
    """
    Ppc = 677.0 + 15.0 * gama_g - 37.5 * gama_g ** 2
    Tpc = 168.0 + 325.0 * gama_g - 12.5 * gama_g ** 2
    return Ppc, Tpc


def standing_humido(gama_g: float):
    """Standing (1977) – Gás Natural Húmido / Condensado.

    Args:
        gama_g: Densidade relativa do gás (ar = 1)
    Returns:
        (Ppc [psia], Tpc [°R])
    """
    Ppc = 706.0 - 51.7 * gama_g - 11.1 * gama_g ** 2
    Tpc = 187.0 + 330.0 * gama_g - 71.5 * gama_g ** 2
    return Ppc, Tpc


def sutton(gama_g: float):
    """Sutton – Gás Natural Húmido / Condensado.

    Args:
        gama_g: Densidade relativa do gás (ar = 1)
    Returns:
        (Ppc [psia], Tpc [°R])
    """
    Ppc = 169.2 + 349.5 * gama_g - 74.0 * gama_g ** 2
    Tpc = 756.8 - 131.07 * gama_g - 3.6 * gama_g ** 2
    return Ppc, Tpc


# ── Correcções para gases ácidos / não-hidrocarbonetos ─────────────────────────

def wichert_aziz(Ppc: float, Tpc: float, y_co2: float, y_h2s: float):
    """Correcção de Wichert e Aziz (1972) para H2S e CO2.

    Args:
        Ppc:   Pressão pseudo-crítica  [psia]
        Tpc:   Temperatura pseudo-crítica [°R]
        y_co2: Fracção molar de CO2 (0–1)
        y_h2s: Fracção molar de H2S (0–1)
    Returns:
        (Ppc_corr [psia], Tpc_corr [°R])
    """
    S = y_co2 + y_h2s
    if S <= 0.0:
        return Ppc, Tpc

    D = math.sqrt(max(y_h2s, 0.0)) - y_co2 ** 4
    epsilon = 120.0 * (S ** 0.9 - S ** 1.6) + 15.0 * D

    Tpc_corr = Tpc - epsilon
    denom = Tpc + y_h2s * (1.0 - y_h2s) * epsilon
    Ppc_corr = Ppc * Tpc_corr / denom

    return Ppc_corr, Tpc_corr


def carr_kobayashi_burrows(Ppc: float, Tpc: float,
                           y_co2: float, y_h2s: float, y_n2: float):
    """Correcção de Carr, Kobayashi e Burrows (1954) para não-hidrocarbonetos.

    Args:
        Ppc:   Pressão pseudo-crítica  [psia]
        Tpc:   Temperatura pseudo-crítica [°R]
        y_co2: Fracção molar de CO2 (0–1)
        y_h2s: Fracção molar de H2S (0–1)
        y_n2:  Fracção molar de N2  (0–1)
    Returns:
        (Ppc_corr [psia], Tpc_corr [°R])
    """
    Tpc_corr = Tpc - 80.0 * y_co2 + 130.0 * y_h2s - 250.0 * y_n2
    Ppc_corr = Ppc + 440.0 * y_co2 + 600.0 * y_h2s - 170.0 * y_n2
    return Ppc_corr, Tpc_corr
