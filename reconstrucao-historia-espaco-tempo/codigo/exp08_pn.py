"""Experimento 8: nivel B pos-newtoniano (inspiral de 10 Hz ate x = 1/6, sem spins).

Modelos de modos (Blanchet, Living Rev. Relativ. 27, 4 (2024), eq. modedef e seguintes):
  h_lm = 2 eta x sqrt(16 pi/5) H_lm e^{-i m psi}, h_{l,-m} = (-1)^l conj(h_lm)   (M = 1)
  LO : H22 = 1 ;                  xdot = (64/5) eta x^5
  NLO: H22 = 1 + x(-107/42 + 55 eta/42) + 2 pi x^{3/2}
       H21 = (i/3) Delta x^{1/2} ; H33 = -(3/4) i sqrt(15/14) Delta x^{1/2} ; H31 = i Delta x^{1/2}/(12 sqrt 14)
       H32 = (1/3) sqrt(5/7) x (1-3eta) ; H44 = -(8/9) sqrt(5/7) x (1-3eta) ; H42 = sqrt5 x (1-3eta)/63
       xdot ate 2PN (Favata 2009b, eq. xdot35pn truncada).
Memoria de deslocamento antes da janela: LO e 1PN de Favata (eq. H20).

Testes (observador unico, iota = 50 graus, M = 65 M_sol, D = 400 Mpc, janela desde 10 Hz):
  T1 Na ordem dominante, {deslocamento, spin, CM} sao invariantes por (eta, D) -> (lambda eta, lambda D):
     a razao de massas e EXATAMENTE degenerada com essas tres memorias. A giroscopica (~ eta M^2/D^2) quebra.
  T2 Na ordem seguinte, o mesmo par deixa de ser degenerado (diferenca ~ correcoes 1PN).
  T3 Na ordem seguinte, refaco o ajuste (M, D, iota) com eta_B fixo: a familia degenerada continua a
     existir, deformada.
Saida: resultados/exp08_pn.txt
"""
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(__file__))
from memorias import CalculadoraMemoria, gram           # noqa: E402
from harmonicos import sYlm, Dfrak, ethb2_de_escalar     # noqa: E402
from binarias import favata_h20, lrr_h40                 # noqa: E402
from deteccao import MSUN_S, MPC_S                       # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


LISTA = {"LO": [(2, 2), (2, -2)],
         "NLO": [(2, 2), (2, -2), (2, 1), (2, -1), (3, 3), (3, -3), (3, 1), (3, -1), (3, 2), (3, -2),
                 (4, 4), (4, -4), (4, 2), (4, -2)]}
_calc = {k: CalculadoraMemoria(v) for k, v in LISTA.items()}


def xdot(x, eta, ordem):
    base = 64 / 5 * eta * x ** 5
    if ordem == "LO":
        return base
    return base * (1 + x * (-743 / 336 - 11 / 4 * eta) + 4 * np.pi * x ** 1.5
                   + x ** 2 * (34103 / 18144 + 13661 / 2016 * eta + 59 / 18 * eta ** 2))


def modos(eta, x0, ordem, xf=1 / 6, dt=0.5):
    xs = np.linspace(x0, xf, 400001)
    dtdx = 1 / xdot(xs, eta, ordem)
    t = np.concatenate([[0], np.cumsum(0.5 * (dtdx[1:] + dtdx[:-1]) * np.diff(xs))])
    phi = np.concatenate([[0], np.cumsum(0.5 * ((xs[1:] ** 1.5) * dtdx[1:] + (xs[:-1] ** 1.5) * dtdx[:-1]) * np.diff(xs))])
    tt = np.arange(0, t[-1], dt)
    x = np.interp(tt, t, xs)
    ph = np.interp(tt, t, phi)
    D = np.sqrt(max(1 - 4 * eta, 0))
    H = {(2, 2): np.ones_like(x)}
    if ordem == "NLO":
        H[(2, 2)] = 1 + x * (-107 / 42 + 55 * eta / 42) + 2 * np.pi * x ** 1.5
        H[(2, 1)] = 1j / 3 * D * x ** 0.5
        H[(3, 3)] = -0.75j * np.sqrt(15 / 14) * D * x ** 0.5
        H[(3, 1)] = 1j * D * x ** 0.5 / (12 * np.sqrt(14))
        H[(3, 2)] = np.sqrt(5 / 7) / 3 * x * (1 - 3 * eta)
        H[(4, 4)] = -8 / 9 * np.sqrt(5 / 7) * x * (1 - 3 * eta)
        H[(4, 2)] = np.sqrt(5) / 63 * x * (1 - 3 * eta)
    hm = {}
    for (l, m), Hl in H.items():
        v = 2 * eta * x * np.sqrt(16 * np.pi / 5) * Hl * np.exp(-1j * m * ph)
        hm[(l, m)] = v
        hm[(l, -m)] = (-1) ** l * np.conj(v)
    return tt, hm, x


def memorias_pn(eta, M_msun, ordem, f_fis=10.0):
    x0 = (np.pi * M_msun * MSUN_S * f_fis) ** (2 / 3)
    t, hm, x = modos(eta, x0, ordem)
    lista = LISTA[ordem]
    Hm = np.stack([hm[k] for k in lista], axis=1)
    Hd = np.gradient(Hm, t[1] - t[0], axis=0, edge_order=2)
    m = _calc[ordem].memorias_gram(*gram(Hm, Hd, t[1] - t[0]))
    E = m["energia_total"]
    # deslocamento antes da janela
    if ordem == "LO":
        pre20 = 8 * np.sqrt(np.pi / 5) * eta * x0 * 5 / (14 * np.sqrt(6))
        pre40 = 8 * np.sqrt(np.pi / 5) * eta * x0 / (504 * np.sqrt(2))
        E += 0.5 * eta * x0
    else:
        pre20 = 8 * np.sqrt(np.pi / 5) * eta * x0 * 5 / (14 * np.sqrt(6)) * (1 + x0 * (-4075 / 4032 + 67 / 48 * eta))
        pre40 = lrr_h40(x0, eta)
        E += 0.5 * eta * x0 * (1 + x0 * (-0.75 - eta / 12))
    m["deslocamento"][(2, 0)] += pre20
    m["deslocamento"][(4, 0)] += pre40
    Mf = 1 - E
    for (l, mm), dJ in list(m["deslocamento"].items()):
        if mm == 0 and l >= 2:
            dK = -1.5 * Mf * (2 * dJ / ethb2_de_escalar(l)) / Dfrak(l)
            m["cm"][(l, mm)] = m["cm"][(l, mm)] + 0.5 * ethb2_de_escalar(l) * dK
    return m


def observador(m, iota, M_msun, D_mpc):
    Ms, Ds = M_msun * MSUN_S, D_mpc * MPC_S
    out = {}
    for tipo, pot in (("deslocamento", (1, 1)), ("spin", (2, 1)), ("cm", (2, 1)), ("giroscopica", (2, 2))):
        s = 0 if tipo == "giroscopica" else -2
        z = sum(c * sYlm(s, l, mm, iota, 0.0) for (l, mm), c in m[tipo].items() if mm == 0 and l <= 8)
        val = -np.imag(z) if tipo == "spin" else np.real(z)
        out[tipo] = float(val) * Ms ** pot[0] / Ds ** pot[1]
    return out


def dif(a, b, chaves):
    return {k: (b[k] - a[k]) / abs(a[k]) for k in chaves}


if __name__ == "__main__":
    qA, qB = 1.2, 3.0
    etaA, etaB = qA / (1 + qA) ** 2, qB / (1 + qB) ** 2
    lam = etaB / etaA
    MA, DA, iA = 65.0, 400.0, np.radians(50.0)
    TRES = ("deslocamento", "spin", "cm")
    QUATRO = TRES + ("giroscopica",)
    log("Par: A (q = %.1f, eta = %.4f, D = %.0f Mpc) e B (q = %.1f, eta = %.4f, D = %.1f Mpc = lambda D_A, lambda = %.4f); M = %.0f, iota = 50 graus"
        % (qA, etaA, DA, qB, etaB, lam * DA, lam, MA))
    for ordem in ("LO", "NLO"):
        mA = memorias_pn(etaA, MA, ordem)
        mB = memorias_pn(etaB, MA, ordem)
        vA = observador(mA, iA, MA, DA)
        vB = observador(mB, iA, MA, lam * DA)
        d = dif(vA, vB, QUATRO)
        log("%-3s: diferenca relativa B - A: %s" % (ordem, ", ".join("%s %+.2e" % (k, v) for k, v in d.items())))
    # T3: ordem seguinte, ajuste de (M_B, D_B, iota_B) com eta_B fixo usando as tres memorias mensuraveis
    mA = memorias_pn(etaA, MA, "NLO")
    vA = observador(mA, iA, MA, DA)
    _c = {}

    def res(p, chaves):
        MB, DB, iB = p
        k = round(MB, 10)
        if k not in _c:
            _c[k] = memorias_pn(etaB, MB, "NLO")
        vB = observador(_c[k], iB, MB, DB)
        return np.array([dif(vA, vB, chaves)[c] for c in chaves])

    r3 = least_squares(lambda p: res(p, TRES), [MA, lam * DA, iA], bounds=([20, 50, 0.05], [200, 2000, np.pi - 0.05]),
                       xtol=1e-14, ftol=1e-14, diff_step=1e-6)
    log("NLO, so deslocamento + spin + CM: ajuste de B com q = 3 fixo -> M_B = %.3f, D_B = %.2f Mpc, iota_B = %.3f graus, residuo max = %.1e"
        % (r3.x[0], r3.x[1], np.degrees(r3.x[2]), np.max(np.abs(r3.fun))))
    log("     giroscopica nesse ponto: diferenca relativa = %+.3f" % (res(r3.x, QUATRO)[3]))
    r4 = least_squares(lambda p: res(p, QUATRO), r3.x, bounds=([20, 50, 0.05], [200, 2000, np.pi - 0.05]),
                       xtol=1e-14, ftol=1e-14, diff_step=1e-6)
    log("NLO, as quatro memorias com q = 3 fixo e (M, D, iota) livres: residuo max = %.2e (3 incognitas, 4 equacoes)"
        % np.max(np.abs(r4.fun)))
    with open(os.path.join(AQUI, "..", "resultados", "exp08_pn.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
