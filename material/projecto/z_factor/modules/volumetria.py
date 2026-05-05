"""
Factor Volume de Formação do Gás (Bg) e Factor de Expansão do Gás (Eg).

Condições padrão (standard):  P_sc = 14,696 psia  |  T_sc = 519,67 °R (60 °F)

Unidades disponíveis:
  Bg :  ft³/scf   |  bbl/Mscf   |  m³/m³
  Eg :  scf/ft³   |  Mscf/bbl   |  m³/m³

Equação base:
    Bg [ft³/scf] = (P_sc / T_sc) × Z × T / P  ≈  0,02829 × Z × T[°R] / P[psia]

Referência: Ramos, G. (2020). Indústria do Gás Natural, Vol. 2. ISPTEC.
"""

# ── Condições padrão ─────────────────────────────────────────────────────────
_P_SC = 14.696    # psia
_T_SC = 519.67    # °R  (60 °F + 459,67)


def _bg_base(Z: float, T_R: float, P: float) -> float:
    """Bg em ft³/scf (fórmula base para todas as conversões)."""
    return (_P_SC / _T_SC) * Z * T_R / P   # ≈ 0,02829 Z T / P


# ── Factor Volume de Formação (Bg) ────────────────────────────────────────────

def bg_ft3_scf(Z: float, T_R: float, P: float) -> float:
    """
    Factor Volume de Formação do Gás em ft³/scf.

    Args:
        Z:   Factor de compressibilidade
        T_R: Temperatura [°R]
        P:   Pressão [psia]
    Returns:
        Bg [ft³/scf]
    """
    return _bg_base(Z, T_R, P)


def bg_bbl_Mscf(Z: float, T_R: float, P: float) -> float:
    """
    Factor Volume de Formação do Gás em bbl/Mscf.

    Conversão: 1 bbl = 5,61458 ft³  |  1 Mscf = 1000 scf
    """
    return _bg_base(Z, T_R, P) * 1000.0 / 5.61458


def bg_m3_m3(Z: float, T_R: float, P: float) -> float:
    """
    Factor Volume de Formação do Gás em m³(res)/m³(std).

    Numericamente equivalente a ft³/scf pois a razão de volumes
    cancela as conversões ft→m.
    """
    return _bg_base(Z, T_R, P)


# ── Factor de Expansão do Gás (Eg) ────────────────────────────────────────────

def eg_scf_ft3(Z: float, T_R: float, P: float) -> float:
    """Factor de Expansão em scf/ft³  =  1 / Bg[ft³/scf]."""
    return 1.0 / _bg_base(Z, T_R, P)


def eg_Mscf_bbl(Z: float, T_R: float, P: float) -> float:
    """Factor de Expansão em Mscf/bbl  =  1 / Bg[bbl/Mscf]."""
    return 1.0 / bg_bbl_Mscf(Z, T_R, P)


def eg_m3_m3(Z: float, T_R: float, P: float) -> float:
    """Factor de Expansão em m³(std)/m³(res)  =  1 / Bg[m³/m³]."""
    return 1.0 / _bg_base(Z, T_R, P)
