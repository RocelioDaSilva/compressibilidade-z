"""
Correlações de viscosidade do gás natural.

Correlações implementadas:
  1. Lee, González e Eakin (1966) — LGE
  2. Lucas et al. (1981)

Referência: Ramos, G. (2020). Indústria do Gás Natural, Vol. 2. ISPTEC.
"""

import math


# ── Utilitários internos ──────────────────────────────────────────────────────

def _peso_molecular(gama_g: float) -> float:
    """Peso molecular aparente do gás [lb/lb-mol]."""
    return 28.97 * gama_g


def _densidade_gcc(Mg: float, P: float, Z: float, T_R: float) -> float:
    """
    Densidade do gás em g/cm³.

    Equação de estado real:  ρ [lb/ft³] = Mg P / (R Z T)
    com R = 10,73 psia·ft³/(lb-mol·°R).
    """
    rho_lbft3 = Mg * P / (10.73 * Z * T_R)
    return rho_lbft3 * 0.016018   # lb/ft³ → g/cm³


# ── 1. Lee, González e Eakin (1966) ──────────────────────────────────────────

def viscosidade_lee_gonzalez_eakin(T_R: float, P: float,
                                    Z: float, gama_g: float) -> float:
    """
    Correlação de Lee, González e Eakin (1966) para a viscosidade do gás natural.

    Equações:
        Mg  = 28,97 γg
        ρg  = Mg P / (10,73 Z T)          [lb/ft³]
        ρg  → g/cm³  (× 0,016018)

        K   = (9,4 + 0,02 Mg) T^1.5 / (209 + 19 Mg + T)
        X   = 3,5 + 986/T + 0,01 Mg
        Y   = 2,4 − 0,2 X
        μg  = K × exp(X × ρg^Y) × 10⁻⁴   [cP]

    Args:
        T_R:    Temperatura [°R]
        P:      Pressão [psia]
        Z:      Factor de compressibilidade
        gama_g: Densidade relativa do gás (ar = 1)
    Returns:
        Viscosidade [cP]
    """
    Mg  = _peso_molecular(gama_g)
    rho = _densidade_gcc(Mg, P, Z, T_R)

    K = (9.4 + 0.02 * Mg) * T_R ** 1.5 / (209.0 + 19.0 * Mg + T_R)
    X = 3.5 + 986.0 / T_R + 0.01 * Mg
    Y = 2.4 - 0.2 * X

    return K * math.exp(X * rho ** Y) * 1.0e-4   # cP


# ── 2. Lucas et al. (1981) ────────────────────────────────────────────────────

def viscosidade_lucas(T_R: float, P: float,
                      Ppc: float, Tpc: float, gama_g: float) -> float:
    """
    Correlação de Lucas et al. (1981) para a viscosidade do gás natural.

    Equações:
        Mg  = 28,97 γg
        Tpr = T / Tpc
        Ppr = P / Ppc

        ξ   = 0,176 × (Tpc_K / (Mg³ × Ppc_bar⁴))^(1/6)   [μP⁻¹]

        μ₁·ξ = 0,807 Tpr^0.618 − 0,357 exp(−0,449 Tpr)
              + 0,340 exp(−4,058 Tpr) + 0,018
        μ₁  = (μ₁·ξ) / ξ × 10⁻⁴            [cP]  (μP → cP)

    Correcção de pressão (Ahmed, 2010):
        a₁ = 1,245×10⁻³ exp(5,1726 Tpr^−0.3286) / Tpr
        a₂ = a₁ (1,6553 Tpr − 1,2723)
        a₃ = 0,4489 exp(3,0578 Tpr^−37.7332)
        a₄ = 1,7368 exp(2,2310 Tpr^−7.6351)
        μg/μ₁ = 1 + a₁ Ppr^1.3088 / (a₂ Ppr^1.3088 + (1 + a₃ Ppr^a₄)⁻¹)

    Args:
        T_R:    Temperatura [°R]
        P:      Pressão [psia]
        Ppc:    Pressão pseudo-crítica [psia]
        Tpc:    Temperatura pseudo-crítica [°R]
        gama_g: Densidade relativa do gás (ar = 1)
    Returns:
        Viscosidade [cP]
    """
    Mg  = _peso_molecular(gama_g)
    Tpr = T_R / Tpc
    Ppr = P   / Ppc

    # Converter Tpc → K e Ppc → bar para o parâmetro ξ
    Tpc_K   = Tpc * 5.0 / 9.0
    Ppc_bar = Ppc * 0.0689476

    # Parâmetro de redução da viscosidade (Stiel-Thodos)
    # ξ [μP^-1] = 0,176 × (Tpc_K / (Mg³ × Ppc_bar⁴))^(1/6)
    xi = 0.176 * (Tpc_K / (Mg ** 3 * Ppc_bar ** 4)) ** (1.0 / 6.0)

    # Viscosidade à pressão de 1 atm
    mu1_xi = (0.807 * Tpr ** 0.618
              - 0.357 * math.exp(-0.449 * Tpr)
              + 0.340 * math.exp(-4.058 * Tpr)
              + 0.018)
    mu1 = (mu1_xi / xi) * 1.0e-4   # μP → cP

    if Ppr <= 1.0e-6:
        return mu1

    # Correcção de pressão
    a1 = 1.245e-3 * math.exp(5.1726 * Tpr ** (-0.3286)) / Tpr
    a2 = a1 * (1.6553 * Tpr - 1.2723)
    a3 = 0.4489 * math.exp(3.0578 * Tpr ** (-37.7332))
    a4 = 1.7368 * math.exp(2.2310 * Tpr ** (-7.6351))

    ratio = (1.0 + a1 * Ppr ** 1.3088
             / (a2 * Ppr ** 1.3088 + (1.0 + a3 * Ppr ** a4) ** (-1.0)))

    return mu1 * ratio
