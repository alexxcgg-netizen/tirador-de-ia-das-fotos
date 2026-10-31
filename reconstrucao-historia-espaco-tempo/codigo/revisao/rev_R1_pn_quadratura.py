"""Revisao R1: memorias m = 0 de uma inspiral PN por quadratura em x (sem amostrar o tempo).

Para saidas m = 0 so contam pares de modos com o mesmo m, cujo produto nao oscila. Entao
    B_jk = int hdot_j conj(hdot_k) du,  A_jk = int h_j conj(hdot_k) du   (m_j = m_k)
podem ser calculados como integrais em x com du = dx / xdot, com precisao de maquina e para janelas
que comecam em x_i muito pequeno. Os modos e o xdot sao os do exp08 (Blanchet 2024, ate 1PN nos modos).
As matrizes vao para CalculadoraMemoria.memorias_gram (o mesmo codigo do 07).

Testes:
  Q0  conferencia contra as formulas fechadas (Favata h20, Nichols S30, Faye-Seraj giroscopica).
  Q1  (secao 1.3, item b) divergencia de cada memoria quando a janela recua (x_i -> 0), LO e NLO;
      a giroscopica separada nos seus dois termos.
  Q2  (secao 2.3, item e) escala com eta na ordem dominante: cada memoria / eta e constante?
      Parte nula do CM; parte ordinaria com M_f (como no codigo) e com M (massa total).
  Q3  (secao 3.4 / exp08) o par (eta, D) -> (lambda eta, lambda D) na ordem dominante, sem erro de grade.
  Q4  (item c) a integral bruta int h_+ du na janela contra a memoria de CM, no observador.
Saida: resultados/revisao/rev_R1_pn_quadratura.txt
"""
import os
import sys

import numpy as np
from scipy.integrate import simpson

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
from memorias import CalculadoraMemoria                  # noqa: E402
from harmonicos import sYlm, Dfrak, ethb2_de_escalar      # noqa: E402
from deteccao import MSUN_S, MPC_S                        # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1_pn_quadratura.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


LISTA = {"LO": [(2, 2), (2, -2)],
         "NLO": [(2, 2), (2, -2), (2, 1), (2, -1), (3, 3), (3, -3), (3, 1), (3, -1), (3, 2), (3, -2),
                 (4, 4), (4, -4), (4, 2), (4, -2)]}
CALC = {k: CalculadoraMemoria(v) for k, v in LISTA.items()}


def xdot(x, eta, ordem):
    base = 64 / 5 * eta * x ** 5
    if ordem == "LO":
        return base
    return base * (1 + x * (-743 / 336 - 11 / 4 * eta) + 4 * np.pi * x ** 1.5
                   + x ** 2 * (34103 / 18144 + 13661 / 2016 * eta + 59 / 18 * eta ** 2))


def Hamp(x, eta, ordem):
    """Amplitudes H_lm(x) (m > 0) como no exp08."""
    D = np.sqrt(max(1 - 4 * eta, 0))
    H = {(2, 2): np.ones_like(x, dtype=complex)}
    if ordem == "NLO":
        H[(2, 2)] = 1 + x * (-107 / 42 + 55 * eta / 42) + 2 * np.pi * x ** 1.5 + 0j
        H[(2, 1)] = 1j / 3 * D * x ** 0.5
        H[(3, 3)] = -0.75j * np.sqrt(15 / 14) * D * x ** 0.5
        H[(3, 1)] = 1j * D * x ** 0.5 / (12 * np.sqrt(14))
        H[(3, 2)] = np.sqrt(5 / 7) / 3 * x * (1 - 3 * eta) + 0j
        H[(4, 4)] = -8 / 9 * np.sqrt(5 / 7) * x * (1 - 3 * eta) + 0j
        H[(4, 2)] = np.sqrt(5) / 63 * x * (1 - 3 * eta) + 0j
    return H


def gram_adiabatico(eta, xi, xf, ordem, n=400001):
    """B e A (so m_j = m_k) por quadratura em x numa grade logaritmica."""
    lista = LISTA[ordem]
    x = np.exp(np.linspace(np.log(xi), np.log(xf), n))
    xd = xdot(x, eta, ordem)
    Om = x ** 1.5
    H = Hamp(x, eta, ordem)
    a, ad = {}, {}
    for (l, m), Hl in H.items():
        amp = 2 * eta * x * np.sqrt(16 * np.pi / 5) * Hl
        damp = np.gradient(amp, x, edge_order=2) * xd                  # d a / du
        a[(l, m)], ad[(l, m)] = amp, damp
        # h_{l,-m} = (-1)^l conj(h_lm): a_{l,-m} = (-1)^l conj(a_lm) com fase e^{+i m psi}
        a[(l, -m)], ad[(l, -m)] = (-1) ** l * np.conj(amp), (-1) ** l * np.conj(damp)
    # hdot_lm = (ad - i m Om a) e^{-i m psi}; o fator de fase cancela nos pares de mesmo m
    hd = {k: ad[k] - 1j * k[1] * Om * a[k] for k in a}
    N = len(lista)
    Bm = np.zeros((N, N), dtype=complex)
    Am = np.zeros((N, N), dtype=complex)
    for j, kj in enumerate(lista):
        for k, kk in enumerate(lista):
            if kj[1] != kk[1]:
                continue
            Bm[j, k] = simpson(hd[kj] * np.conj(hd[kk]) / xd, x=x)
            Am[j, k] = simpson(a[kj] * np.conj(hd[kk]) / xd, x=x)
    E_jan = simpson(sum(np.abs(hd[k]) ** 2 for k in lista) / xd, x=x) / (16 * np.pi)
    return Bm, Am, E_jan


def memorias_m0(eta, xi, xf, ordem):
    Bm, Am, E_jan = gram_adiabatico(eta, xi, xf, ordem)
    m = CALC[ordem].memorias_gram(Bm, Am)
    out = {"J20": m["deslocamento"][(2, 0)].real, "J40": m["deslocamento"][(4, 0)].real,
           "S30": m["spin"][(3, 0)], "Knul20": m["cm"][(2, 0)].real, "Knul40": m["cm"][(4, 0)].real,
           "E_jan": E_jan, "E_mod": m["energia_total"]}
    for l in (1, 3):
        ts = -Dfrak(l) * m["spin_potencial"][(l, 0)] if l >= 2 else 0.0
        out["G%d_spin" % l] = complex(ts).real
        out["G%d_hel" % l] = (0.25 * m["helicidade_modos"][(l, 0)]).real
        out["G%d" % l] = m["giroscopica"][(l, 0)].real
    return out


def antes(x0, eta):
    """Deslocamento acumulado antes da janela (LO), como no exp08."""
    return (8 * np.sqrt(np.pi / 5) * eta * x0 * 5 / (14 * np.sqrt(6)),
            8 * np.sqrt(np.pi / 5) * eta * x0 / (504 * np.sqrt(2)))


def observador(mm, eta, x0, iota, M_msun, D_mpc, massa_cm="Mf"):
    """Quatro memorias no observador (unidades fisicas), deslocamento total, CM com M_f ou M."""
    p20, p40 = antes(x0, eta)
    J = {2: mm["J20"] + p20, 4: mm["J40"] + p40}
    Mf = 1 - (mm["E_mod"] + 0.5 * eta * x0)
    mc = Mf if massa_cm == "Mf" else 1.0
    K = {l: (mm["Knul%d0" % l] - 1.5 * mc * J[l] / Dfrak(l)) for l in (2, 4)}   # nivel de deformacao
    Y = lambda s, l: sYlm(s, l, 0, iota, 0.0).real
    Ms, Ds = M_msun * MSUN_S, D_mpc * MPC_S
    d = sum(J[l] * Y(-2, l) for l in (2, 4))
    s = -(mm["S30"] * Y(-2, 3)).imag
    cm = sum(K[l] * Y(-2, l) for l in (2, 4))
    g = mm["G1"] * Y(0, 1) + mm["G3"] * Y(0, 3)
    return dict(deslocamento=d * Ms / Ds, spin=s * Ms ** 2 / Ds, cm=cm * Ms ** 2 / Ds, giroscopica=g * Ms ** 2 / Ds ** 2)


if __name__ == "__main__":
    # ---------------- Q0
    eta, xi, xf = 0.25, 0.05, 0.20
    mm = memorias_m0(eta, xi, xf, "LO")
    ref_J = 4 / 7 * np.sqrt(5 * np.pi / 6) * eta * (xf - xi)
    ref_S = np.sqrt(3 * np.pi / 70) * eta * abs(xf ** -0.5 - xi ** -0.5)
    th = np.linspace(0.2, 3.0, 9)
    psi0 = 5 * eta / 32
    FS = psi0 * (xf ** -0.5 - xi ** -0.5) * ((np.cos(3 * th) + 7 * np.cos(th)) - 0.6 * (5 * np.cos(3 * th) + 3 * np.cos(th)))
    G = mm["G1"] * sYlm(0, 1, 0, th, 0).real + mm["G3"] * sYlm(0, 3, 0, th, 0).real
    log("Q0 (LO, eta = 1/4, x de 0.05 a 0.20): J20/Favata - 1 = %.1e ; |S30|/Nichols - 1 = %.1e ;"
        " giro: max|cod - FS|/max|FS| = %.1e ; E_jan/(eta(xf-xi)/2) - 1 = %.1e"
        % (mm["J20"] / ref_J - 1, abs(mm["S30"]) / ref_S - 1, np.max(np.abs(G - FS)) / np.max(np.abs(FS)),
           mm["E_jan"] / (0.5 * eta * (xf - xi)) - 1))

    # ---------------- Q1
    log("")
    log("Q1 divergencia quando a janela recua (x_f = 1/6, eta = 0.2479):")
    eta = 1.2 / 2.2 ** 2
    xis = [0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
    for ordem in ("LO", "NLO"):
        tab = [memorias_m0(eta, x_, 1 / 6, ordem) for x_ in xis]
        chaves = ["J20", "J40", "S30", "Knul20", "Knul40", "G1_spin", "G1_hel", "G3_spin", "G3_hel"]
        log("  %s:" % ordem)
        for ch in chaves:
            v = np.array([abs(t[ch]) for t in tab])
            if np.all(v < 1e-14):
                log("    %-8s identicamente nulo (|.| < 1e-14)" % ch)
                continue
            incl = np.log(v[-1] / v[-2]) / np.log(xis[-1] / xis[-2])
            log("    %-8s x_i = %s : %s ; d ln|m| / d ln x_i (x_i -> 0.001) = %+.3f"
                % (ch, xis, " ".join("%.4e" % vv for vv in v), incl))

    # ---------------- Q2
    log("")
    log("Q2 escala com eta na ordem dominante (x_i = 0.0466, x_f = 1/6): memoria / eta")
    x0 = (np.pi * 65 * MSUN_S * 10.0) ** (2 / 3)
    for et in (0.25, 0.2479, 0.2, 0.1875, 0.1):
        mm = memorias_m0(et, x0, 1 / 6, "LO")
        p20, _ = antes(x0, et)
        Mf = 1 - (mm["E_mod"] + 0.5 * et * x0)
        log("  eta = %.4f : J20/eta = %.12f  S30/eta = %.12f  G1/eta = %.12f  G3/eta = %.12f  K_nula20 = %.1e"
            "  K20(M_f)/eta = %.10f  K20(M)/eta = %.10f"
            % (et, mm["J20"] / et, mm["S30"].imag / et, mm["G1"] / et, mm["G3"] / et, mm["Knul20"],
               (mm["Knul20"] - 1.5 * Mf * (mm["J20"] + p20) / Dfrak(2)) / et,
               (mm["Knul20"] - 1.5 * (mm["J20"] + p20) / Dfrak(2)) / et))

    # ---------------- Q3
    log("")
    qA, qB = 1.2, 3.0
    eA, eB = qA / (1 + qA) ** 2, qB / (1 + qB) ** 2
    lam = eB / eA
    MA, DA, iA = 65.0, 400.0, np.radians(50.0)
    for ordem in ("LO", "NLO"):
        mA = memorias_m0(eA, x0, 1 / 6, ordem)
        mB = memorias_m0(eB, x0, 1 / 6, ordem)
        for mc in ("Mf", "M"):
            vA = observador(mA, eA, x0, iA, MA, DA, mc)
            vB = observador(mB, eB, x0, iA, MA, lam * DA, mc)
            log("Q3 %-3s, CM com %-2s: (B - A)/|A| = %s" % (ordem, mc, ", ".join(
                "%s %+.3e" % (k, (vB[k] - vA[k]) / abs(vA[k])) for k in vA)))
    log("   (exp08 LO: deslocamento -1.28e-04, spin +5.94e-05, cm -5.01e-03, giroscopica -3.22e-01)")

    # ---------------- Q4
    log("")
    mA = memorias_m0(eA, x0, 1 / 6, "LO")
    vA = observador(mA, eA, x0, iA, MA, DA)
    p20, p40 = antes(x0, eA)
    # int h^mem_+ du na janela: h_l0(u) = J_l0(x(u)), J_l0 total desde x = 0 ~ kappa_l eta x ; int x du = (5/192)(x_i^-3 - x_f^-3)/eta
    k20, k40 = p20 / (eA * x0), p40 / (eA * x0)
    intx = 5 / 192 * (x0 ** -3 - 6.0 ** 3) / eA
    bruto = (k20 * sYlm(-2, 2, 0, iA, 0).real + k40 * sYlm(-2, 4, 0, iA, 0).real) * eA * intx
    Ms, Ds = MA * MSUN_S, DA * MPC_S
    log("Q4 observador A (LO PN, M = 65, D = 400 Mpc, iota = 50 graus, janela de 10 Hz ate x = 1/6):")
    log("   memoria de CM (definicao de Nichols, como no codigo) = %.3e s ; deslocamento = %.3e"
        % (vA["cm"], vA["deslocamento"]))
    log("   int_{u_i}^{u_f} h_+^{m=0} du (integral bruta da memoria acumulada) = %.3e s  (razao bruta/CM = %.1f)"
        % (bruto * Ms ** 2 / Ds, bruto * Ms ** 2 / Ds / vA["cm"]))
    log("   cada segundo de dados depois da fusao soma Delta h_+ x 1 s = %.3e s a integral bruta" % vA["deslocamento"])
    log("   CM / (M Delta h_+) = %.4f ; previsao da parte ordinaria l = 2 apenas: -M_f/2 = %.4f"
        % (vA["cm"] / (Ms * vA["deslocamento"]), -0.5 * (1 - mA["E_mod"] - 0.5 * eA * x0)))

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(linhas) + "\n")
