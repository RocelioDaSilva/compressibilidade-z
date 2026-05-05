"""
Correlações do factor Z para gás natural.

Métodos implementados:
  1. Gás Ideal              — Z = 1
  2. Hall-Yarborough        — iteração de Newton-Raphson
  3. Dranchuk e Abou-Kassem — iteração de substituição directa

Viscosidade, Bg e Eg estão nos módulos viscosidade.py e volumetria.py.
"""

import math


# ── 1. Gás Ideal ──────────────────────────────────────────────────────────────

def z_ideal() -> float:
    """Gás Ideal: Z = 1."""
    return 1.0


# ── 2. Hall-Yarborough ────────────────────────────────────────────────────────

def z_hall_yarborough(Ppr: float, Tpr: float) -> float:
    """Correlação de Hall-Yarborough para o factor Z (Newton-Raphson).

    Equações:
        t = 1 / Tpr
        A = exp(-1.2 * (1 - t)^2)

        f(y)  = a + b + c + d  = 0
          a = -0.06125 * Ppr * t * A
          b = (y + y² + y³ - y⁴) / (1 - y)³
          c = -((4.58t - 9.76)t + 14.76) * t * y²
          d =  ((42.4t - 242.2)t + 90.7)  * t * y^(2.18 + 2.82t)

        f'(y) = da + db + dc
          da = (y⁴ - 4y³ + 4y² + 4y + 1) / (1 - y)⁴
          db = -((9.16t - 19.52)t + 29.52) * t * y
          dc =  (2.18 + 2.82t) * ((42.4t - 242.2)t + 90.7) * t * y^(1.18 + 2.82t)

        Z = 0.06125 * Ppr * t * A / y

    Args:
        Ppr: Pressão pseudo-reduzida
        Tpr: Temperatura pseudo-reduzida
    Returns:
        Factor Z (float)
    """
    t = 1.0 / Tpr
    A = math.exp(-1.2 * (1.0 - t) ** 2)

    # Estimativa inicial (conforme especificação)
    y = 0.001

    for _ in range(2000):
        # ── f(y) ──────────────────────────────────────────────────────────────
        a = -0.06125 * Ppr * t * A

        # b = (y + y² + y³ - y⁴) / (1 - y)³
        # Forma expandida: (( (-y + 1)*y + 1 )*y + 1)*y / (1 - y)^3
        _b = ((-y + 1.0) * y + 1.0) * y + 1.0
        b = _b * y / (1.0 - y) ** 3

        c = -((4.58 * t - 9.76) * t + 14.76) * t * y ** 2
        d = ((42.4 * t - 242.2) * t + 90.7) * t * y ** (2.18 + 2.82 * t)
        fy = a + b + c + d

        # ── f'(y) ─────────────────────────────────────────────────────────────
        # da = (y⁴ - 4y³ + 4y² + 4y + 1) / (1 - y)^4
        # Forma expandida: (((y - 4)*y + 4)*y + 4)*y + 1) / (1 - y)^4
        da = (((y - 4.0) * y + 4.0) * y + 4.0) * y + 1.0
        da /= (1.0 - y) ** 4

        db = -((9.16 * t - 19.52) * t + 29.52) * t * y
        dc = ((2.18 + 2.82 * t)
              * ((42.4 * t - 242.2) * t + 90.7)
              * t
              * y ** (1.18 + 2.82 * t))
        dfy = da + db + dc

        if abs(dfy) < 1e-15:
            break

        y_new = y - fy / dfy

        if abs(y_new - y) < 1e-5:
            y = y_new
            break

        y = max(y_new, 1e-7)   # manter y estritamente positivo

    return 0.06125 * Ppr * t * A / y


# ── 3. Dranchuk e Abou-Kassem ─────────────────────────────────────────────────

def z_dranchuk_abou_kassem(Ppr: float, Tpr: float) -> float:
    """Correlação de Dranchuk e Abou-Kassem para o factor Z (substituição directa).

    Referência: Dranchuk e Abou-Kassem, 1975.

    Equação:
        ρr  = 0.27 * Ppr / (Z * Tpr)

        Z = 1 + (A1 + A2/Tpr + A3/Tpr³ + A4/Tpr⁴ + A5/Tpr⁵) * ρr
              + (A6 + A7/Tpr + A8/Tpr²) * ρr²
              - A9 * (A7/Tpr + A8/Tpr²) * ρr⁵
              + A10 * (1 + A11*ρr²) * (ρr²/Tpr³) * exp(-A11*ρr²)

    Coeficientes:
        A1  =  0.3265    A2  = -1.0700    A3  = -0.5339
        A4  =  0.01569   A5  = -0.05165   A6  =  0.5475
        A7  = -0.7361    A8  =  0.1844    A9  =  0.1056
        A10 =  0.6134    A11 =  0.7210

    Args:
        Ppr: Pressão pseudo-reduzida
        Tpr: Temperatura pseudo-reduzida
    Returns:
        Factor Z (float)
    """
    A1  =  0.3265
    A2  = -1.0700
    A3  = -0.5339
    A4  =  0.01569
    A5  = -0.05165
    A6  =  0.5475
    A7  = -0.7361
    A8  =  0.1844
    A9  =  0.1056
    A10 =  0.6134
    A11 =  0.7210

    Z = 1.0   # estimativa inicial

    for _ in range(1000):
        rho_r = 0.27 * Ppr / (Z * Tpr)

        c1 = A1 + A2/Tpr + A3/Tpr**3 + A4/Tpr**4 + A5/Tpr**5
        c2 = A6 + A7/Tpr + A8/Tpr**2
        c3 = A9 * (A7/Tpr + A8/Tpr**2)
        c4 = (A10
              * (1.0 + A11 * rho_r**2)
              * (rho_r**2 / Tpr**3)
              * math.exp(-A11 * rho_r**2))

        Z_new = 1.0 + c1*rho_r + c2*rho_r**2 - c3*rho_r**5 + c4

        if abs(Z_new - Z) < 1e-6:
            Z = Z_new
            break

        Z = max(Z_new, 0.1)   # evitar divergência para valores não físicos

    return Z
