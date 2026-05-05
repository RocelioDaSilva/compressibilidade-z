"""
Testes de Validação — Factor Z do Gás Natural
==============================================
Engenharia de Reservatórios I — 2025/2026 — Projecto Nº 1

Execução:
    cd "z_factor"
    python test_calculations.py

Passa se todas as asserções forem satisfeitas (imprime PASSED).
"""

import sys, os, math

sys.path.insert(0, os.path.dirname(__file__))

from modules.properties   import (standing_seco, standing_humido, sutton,
                                   wichert_aziz, carr_kobayashi_burrows)
from modules.correlations import (z_ideal, z_hall_yarborough,
                                   z_dranchuk_abou_kassem)
from modules.viscosidade  import (viscosidade_lee_gonzalez_eakin,
                                   viscosidade_lucas)
from modules.volumetria   import (bg_ft3_scf, bg_bbl_Mscf, bg_m3_m3,
                                   eg_scf_ft3, eg_Mscf_bbl, eg_m3_m3)

# ─────────────────────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0

def check(name, value, expected, tol_rel=1e-3):
    """Verifica se |value - expected| / |expected| <= tol_rel."""
    global PASS, FAIL
    err = abs(value - expected) / max(abs(expected), 1e-15)
    ok = err <= tol_rel
    status = "PASS" if ok else "FAIL"
    if not ok:
        FAIL += 1
        print(f"  [{status}] {name}: got {value:.7g}, expected {expected:.7g}"
              f"  (err={err*100:.3f}%)")
    else:
        PASS += 1
        print(f"  [{status}] {name}: {value:.7g}  (err={err*100:.4f}%)")
    return ok

def check_pair(name, got, expected, tol_rel=1e-3):
    """Verifica um par (Ppc, Tpc) ou (Ppc', Tpc')."""
    ok1 = check(f"{name} Ppc", got[0], expected[0], tol_rel)
    ok2 = check(f"{name} Tpc", got[1], expected[1], tol_rel)
    return ok1 and ok2

# ─────────────────────────────────────────────────────────────────────────────
# 1. PROPRIEDADES PSEUDO-CRÍTICAS
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 1. Propriedades Pseudo-Críticas ═══")

# Standing Seco, γg = 0.75
# Ppc = 677 + 15*0.75 - 37.5*0.75² = 677 + 11.25 - 21.09375 = 667.156 psia
# Tpc = 168 + 325*0.75 - 12.5*0.75² = 168 + 243.75 - 7.031   = 404.719 °R
ppc_ss, tpc_ss = standing_seco(0.75)
check_pair("Standing Seco γg=0.75", (ppc_ss, tpc_ss), (667.156, 404.719))

# Standing Húmido, γg = 0.75
# Ppc = 706 - 51.7*0.75 - 11.1*0.75² = 706 - 38.775 - 6.244 = 660.981 psia
# Tpc = 187 + 330*0.75 - 71.5*0.75² = 187 + 247.5 - 40.219  = 394.281 °R
ppc_sh, tpc_sh = standing_humido(0.75)
check_pair("Standing Húmido γg=0.75", (ppc_sh, tpc_sh), (660.981, 394.281))

# Sutton, γg = 0.75
# Ppc = 756.8 - 131.07*0.75 - 3.6*0.75² = 756.8 - 98.303 - 2.025 = 656.473 psia
# Tpc = 169.2 + 349.5*0.75 - 74.0*0.75² = 169.2 + 262.125 - 41.625 = 389.700 °R
ppc_su, tpc_su = sutton(0.75)
check_pair("Sutton γg=0.75", (ppc_su, tpc_su), (656.473, 389.700))

# Sutton fórmulas NÃO trocadas: Ppc deve ser ~657 psia (maior), Tpc ~390 °R
assert ppc_su > tpc_su, "ERRO: Ppc e Tpc parecem trocados em sutton()"
print("  [PASS] Sutton: Ppc > Tpc (fórmulas não trocadas)")

# ─────────────────────────────────────────────────────────────────────────────
# 2. CORRECÇÕES PARA GASES ÁCIDOS
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 2. Correcções de Acidez ═══")

# Wichert-Aziz: Standing Seco γg=0.75, CO2=5%, H2S=10%
# S = 0.15, D = sqrt(0.10) - 0.05^4 ≈ 0.316221
# ε = 120*(0.15^0.9 - 0.15^1.6) + 15*D ≈ 20.748
# Tpc' = 404.719 - 20.748 = 383.971 °R
# Ppc' = 667.156 * 383.971 / (404.719 + 0.10*0.90*20.748) ≈ 630.0 psia
ppc_wa, tpc_wa = wichert_aziz(ppc_ss, tpc_ss, 0.05, 0.10)
check("Wichert-Aziz Ppc'", ppc_wa, 630.0, tol_rel=2e-3)
check("Wichert-Aziz Tpc'", tpc_wa, 383.97, tol_rel=1e-3)

# Wichert-Aziz gás doce (y_CO2=y_H2S=0): deve ser identidade
ppc_nd, tpc_nd = wichert_aziz(ppc_ss, tpc_ss, 0.0, 0.0)
check("Wichert-Aziz gás doce Ppc'", ppc_nd, ppc_ss, tol_rel=1e-9)
check("Wichert-Aziz gás doce Tpc'", tpc_nd, tpc_ss, tol_rel=1e-9)

# Carr-Kobayashi-Burrows: Standing Seco γg=0.75, CO2=5%, H2S=10%, N2=0%
# Tpc' = 404.719 - 80*0.05 + 130*0.10 - 250*0 = 404.719 - 4 + 13 = 413.719 °R
# Ppc' = 667.156 + 440*0.05 + 600*0.10 - 170*0 = 667.156 + 22 + 60 = 749.156 psia
ppc_ck, tpc_ck = carr_kobayashi_burrows(ppc_ss, tpc_ss, 0.05, 0.10, 0.0)
check("Carr-KB Ppc'", ppc_ck, 749.156, tol_rel=1e-5)
check("Carr-KB Tpc'", tpc_ck, 413.719, tol_rel=1e-5)

# Carr-KB gás doce: deve ser identidade
ppc_ckd, tpc_ckd = carr_kobayashi_burrows(ppc_ss, tpc_ss, 0.0, 0.0, 0.0)
check("Carr-KB gás doce Ppc'", ppc_ckd, ppc_ss, tol_rel=1e-9)
check("Carr-KB gás doce Tpc'", tpc_ckd, tpc_ss, tol_rel=1e-9)

# ─────────────────────────────────────────────────────────────────────────────
# 3. FACTOR Z — GÁS IDEAL
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 3. Factor Z — Gás Ideal ═══")
check("Z ideal", z_ideal(), 1.0, tol_rel=0.0)

# ─────────────────────────────────────────────────────────────────────────────
# 4. FACTOR Z — HALL-YARBOROUGH
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 4. Factor Z — Hall-Yarborough ═══")

# Baixa pressão / alta temperatura: Z ≈ 1
Z_hy_lp = z_hall_yarborough(0.5, 2.0)
assert 0.95 < Z_hy_lp < 1.05, f"Z_HY(Ppr=0.5, Tpr=2.0)={Z_hy_lp:.6f} fora do esperado"
print(f"  [PASS] Z_HY(Ppr=0.5, Tpr=2.0) = {Z_hy_lp:.6f}  (esperado ~1)")

# Caso de referência do enunciado: Standing Seco + Wichert-Aziz
# T=150°F (T_R=609.67°R), P=3300 psia, γg=0.75, CO2=5%, H2S=10%
# Ppc'=630.0 psia, Tpc'=383.97°R → Tpr=1.588, Ppr=5.238
T_R_ref = 150.0 + 459.67
P_ref   = 3300.0
Tpr_ref = T_R_ref / tpc_wa
Ppr_ref = P_ref   / ppc_wa
Z_hy_ref = z_hall_yarborough(Ppr_ref, Tpr_ref)
check("Z_HY caso de referência (Standing+W-A, P=3300)", Z_hy_ref, 0.850981, tol_rel=1e-4)

# Verificação interna: Z = 0.06125*Ppr*t*A/y > 0 sempre
assert Z_hy_ref > 0, "Z_HY deve ser positivo"

# Condição limite Tpr → alta: Z deve tender para 1
Z_hy_ht = z_hall_yarborough(1.0, 3.0)
assert 0.97 < Z_hy_ht < 1.03, f"Z_HY(Ppr=1.0, Tpr=3.0)={Z_hy_ht:.6f} deveria estar perto de 1"
print(f"  [PASS] Z_HY(Ppr=1.0, Tpr=3.0) = {Z_hy_ht:.6f}  (esperado ~1)")

# Sutton + Wichert-Aziz: deve reproduzir o valor de referência do enunciado
ppc_su_wa, tpc_su_wa = wichert_aziz(ppc_su, tpc_su, 0.05, 0.10)
Tpr_su = T_R_ref / tpc_su_wa
Ppr_su = P_ref   / ppc_su_wa
Z_hy_sutton = z_hall_yarborough(Ppr_su, Tpr_su)
check("Z_HY Sutton+W-A vs referência 0.877274", Z_hy_sutton, 0.877274, tol_rel=5e-4)

# ─────────────────────────────────────────────────────────────────────────────
# 5. FACTOR Z — DRANCHUK E ABOU-KASSEM
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 5. Factor Z — Dranchuk e Abou-Kassem ═══")

Z_dak_lp = z_dranchuk_abou_kassem(0.5, 2.0)
assert 0.95 < Z_dak_lp < 1.05, f"Z_DAK(Ppr=0.5, Tpr=2.0)={Z_dak_lp:.6f} fora do esperado"
print(f"  [PASS] Z_DAK(Ppr=0.5, Tpr=2.0) = {Z_dak_lp:.6f}  (esperado ~1)")

Z_dak_ref = z_dranchuk_abou_kassem(Ppr_ref, Tpr_ref)
check("Z_DAK caso de referência (Standing+W-A, P=3300)", Z_dak_ref, 0.853426, tol_rel=1e-4)

assert Z_dak_ref > 0, "Z_DAK deve ser positivo"

# Sutton + Wichert-Aziz
Z_dak_sutton = z_dranchuk_abou_kassem(Ppr_su, Tpr_su)
check("Z_DAK Sutton+W-A vs referência 0.879831", Z_dak_sutton, 0.879831, tol_rel=5e-4)

# HY e DAK devem concordar dentro de 1%
diff_pct = abs(Z_hy_ref - Z_dak_ref) / Z_dak_ref * 100
assert diff_pct < 1.0, f"HY e DAK divergem {diff_pct:.2f}% > 1%"
print(f"  [PASS] HY vs DAK diferença: {diff_pct:.3f}%  (< 1%)")

# ─────────────────────────────────────────────────────────────────────────────
# 6. VISCOSIDADE — LEE, GONZÁLEZ E EAKIN
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 6. Viscosidade — Lee, González e Eakin ═══")

# Caso de referência: T=150°F, P=3300 psia, Z=Z_hy_ref, γg=0.75
mu_lge = viscosidade_lee_gonzalez_eakin(T_R_ref, P_ref, Z_hy_ref, 0.75)
check("μg LGE (P=3300, T=150°F, γg=0.75)", mu_lge, 0.023041, tol_rel=2e-3)
assert 0.005 < mu_lge < 0.1, f"μg={mu_lge:.6f} cP fora do intervalo físico esperado"

# A viscosidade deve crescer com a pressão a T fixo
mu_low  = viscosidade_lee_gonzalez_eakin(T_R_ref, 1000.0, 0.90, 0.75)
mu_high = viscosidade_lee_gonzalez_eakin(T_R_ref, 5000.0, 0.85, 0.75)
assert mu_high > mu_low, "μg deve crescer com P"
print(f"  [PASS] μg cresce com P: {mu_low:.6f} → {mu_high:.6f} cP")

# ─────────────────────────────────────────────────────────────────────────────
# 7. VISCOSIDADE — LUCAS ET AL.
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 7. Viscosidade — Lucas et al. ═══")

mu_lucas = viscosidade_lucas(T_R_ref, P_ref, ppc_wa, tpc_wa, 0.75)
assert 0.005 < mu_lucas < 0.1, f"μg Lucas={mu_lucas:.6f} cP fora do intervalo físico"
print(f"  [PASS] μg Lucas (P=3300, T=150°F) = {mu_lucas:.6f} cP")

# LGE e Lucas devem dar resultados na mesma ordem de grandeza (dentro de 30%)
diff_visc = abs(mu_lge - mu_lucas) / mu_lge
assert diff_visc < 0.30, f"LGE vs Lucas divergem {diff_visc*100:.1f}% > 30%"
print(f"  [PASS] LGE vs Lucas: {diff_visc*100:.1f}% de diferença (< 30%)")

# ─────────────────────────────────────────────────────────────────────────────
# 8. BG E EG — FACTOR VOLUME DE FORMAÇÃO E DE EXPANSÃO
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 8. Bg e Eg ═══")

Z_bg = Z_hy_ref
Bg_ft3  = bg_ft3_scf(Z_bg, T_R_ref, P_ref)
Bg_bbl  = bg_bbl_Mscf(Z_bg, T_R_ref, P_ref)
Bg_m3   = bg_m3_m3(Z_bg, T_R_ref, P_ref)
Eg_scf  = eg_scf_ft3(Z_bg, T_R_ref, P_ref)
Eg_Mscf = eg_Mscf_bbl(Z_bg, T_R_ref, P_ref)
Eg_m3   = eg_m3_m3(Z_bg, T_R_ref, P_ref)

# Bg = (14.696/519.67) * Z * T / P
Bg_expected = (14.696 / 519.67) * Z_bg * T_R_ref / P_ref
check("Bg ft³/scf (fórmula base)", Bg_ft3, Bg_expected, tol_rel=1e-6)
check("Bg ft³/scf vs caso de referência", Bg_ft3, 0.004446, tol_rel=2e-3)

# Eg = 1/Bg
check("Eg = 1/Bg", Eg_scf, 1.0 / Bg_ft3, tol_rel=1e-9)
check("Eg scf/ft³ vs caso de referência", Eg_scf, 224.92, tol_rel=2e-3)

# Conversão ft³/scf → bbl/Mscf: 1 bbl = 5.61458 ft³, 1 Mscf = 1000 scf
Bg_bbl_manual = Bg_ft3 * 1000.0 / 5.61458
check("Bg bbl/Mscf conversão", Bg_bbl, Bg_bbl_manual, tol_rel=1e-9)

# Inversas consistentes
check("Eg Mscf/bbl = 1/Bg_bbl_Mscf", Eg_Mscf, 1.0 / Bg_bbl, tol_rel=1e-9)
check("Eg m³/m³ = 1/Bg_m³_m³", Eg_m3, 1.0 / Bg_m3, tol_rel=1e-9)

# Bg m³/m³ numericamente igual a ft³/scf (razão cancela)
check("Bg m³/m³ ≡ ft³/scf numericamente", Bg_m3, Bg_ft3, tol_rel=1e-9)

# ─────────────────────────────────────────────────────────────────────────────
# 9. PIPELINE COMPLETO — TABELA DO ENUNCIADO
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 9. Pipeline Completo — Tabela do Enunciado ═══")
# T=150°F, γg=0.75, CO2=5%, H2S=10%, N2=0%  (Standing Seco + Wichert-Aziz)
# Valores esperados da tabela no relatório

expected_table = [
    # (P, Z_HY, Z_DAK, mu_LGE, Bg_ft3, Eg_scf)  — valores do código correcto
    (3000, 0.833752, 0.836618, 0.021660, 0.004792, 208.70),
    (3050, 0.836322, 0.839141, 0.021892, 0.004728, 211.52),
    (3100, 0.839020, 0.841782, 0.022124, 0.004666, 214.30),
    (3300, 0.850981, 0.853426, 0.023041, 0.004446, 224.92),
]

all_ok = True
for P, exp_ZHY, exp_ZDAK, exp_mu, exp_Bg, exp_Eg in expected_table:
    Ppr_ = P / ppc_wa
    Z_hy_  = z_hall_yarborough(Ppr_, Tpr_ref)
    Z_dak_ = z_dranchuk_abou_kassem(Ppr_, Tpr_ref)
    mu_    = viscosidade_lee_gonzalez_eakin(T_R_ref, P, Z_hy_, 0.75)
    Bg_    = bg_ft3_scf(Z_hy_, T_R_ref, P)
    Eg_    = eg_scf_ft3(Z_hy_, T_R_ref, P)

    ok = (abs(Z_hy_  - exp_ZHY) / exp_ZHY < 1e-4
       and abs(Z_dak_ - exp_ZDAK)/ exp_ZDAK < 1e-4
       and abs(mu_    - exp_mu)  / exp_mu   < 2e-3
       and abs(Bg_    - exp_Bg)  / exp_Bg   < 2e-3
       and abs(Eg_    - exp_Eg)  / exp_Eg   < 2e-3)
    if not ok:
        FAIL += 1
        all_ok = False
        print(f"  [FAIL] P={P:.0f}: "
              f"ZHY={Z_hy_:.6f}(exp={exp_ZHY}), "
              f"ZDAK={Z_dak_:.6f}(exp={exp_ZDAK}), "
              f"mu={mu_:.6f}(exp={exp_mu}), "
              f"Bg={Bg_:.6f}(exp={exp_Bg}), "
              f"Eg={Eg_:.2f}(exp={exp_Eg})")
    else:
        PASS += 1
        print(f"  [PASS] P={P:.0f} psia: Z_HY={Z_hy_:.6f}, Z_DAK={Z_dak_:.6f}, "
              f"μg={mu_:.6f} cP, Bg={Bg_:.6f} ft³/scf, Eg={Eg_:.2f} scf/ft³")

# ─────────────────────────────────────────────────────────────────────────────
# 10. VERIFICAÇÕES DE SANIDADE FÍSICA
# ─────────────────────────────────────────────────────────────────────────────
print("\n═══ 10. Verificações de Sanidade Física ═══")

# Z deve estar no intervalo razoável (0.1 – 3.0) para Ppr 0.2–15, Tpr 1.1–3.0
bounds_ok = True
for Ppr in [0.2, 1.0, 3.0, 5.0, 8.0, 12.0]:
    for Tpr in [1.1, 1.5, 2.0, 3.0]:
        try:
            Zhy  = z_hall_yarborough(Ppr, Tpr)
            Zdak = z_dranchuk_abou_kassem(Ppr, Tpr)
            if not (0.1 < Zhy < 3.0 and 0.1 < Zdak < 3.0):
                print(f"  [FAIL] Z fora de [0.1,3.0]: Ppr={Ppr}, Tpr={Tpr},"
                      f" Z_HY={Zhy:.4f}, Z_DAK={Zdak:.4f}")
                FAIL += 1
                bounds_ok = False
        except Exception as e:
            print(f"  [FAIL] Excepção em Ppr={Ppr}, Tpr={Tpr}: {e}")
            FAIL += 1
            bounds_ok = False
if bounds_ok:
    PASS += 1
    print("  [PASS] Z ∈ (0.1, 3.0) para toda a grelha Ppr×Tpr testada")

# Bg deve ser positivo e crescer com Z e T, decrescer com P
Bg_1 = bg_ft3_scf(0.9, 650.0, 3000.0)
Bg_2 = bg_ft3_scf(0.9, 650.0, 4000.0)
assert Bg_1 > Bg_2 > 0, "Bg deve decrescer com P"
PASS += 1
print(f"  [PASS] Bg decresce com P: Bg(3000)={Bg_1:.6f} > Bg(4000)={Bg_2:.6f}")

# μg deve ser positiva
assert mu_lge > 0 and mu_lucas > 0
PASS += 1
print(f"  [PASS] μg > 0 (LGE={mu_lge:.6f} cP, Lucas={mu_lucas:.6f} cP)")

# ─────────────────────────────────────────────────────────────────────────────
# RESUMO
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'═'*50}")
print(f"  RESULTADO FINAL: {PASS} PASSED  |  {FAIL} FAILED")
print(f"{'═'*50}")
if FAIL == 0:
    print("  ✓ Todos os testes passaram com sucesso!")
else:
    print(f"  ✗ {FAIL} testes falharam — verificar saída acima.")
    sys.exit(1)
