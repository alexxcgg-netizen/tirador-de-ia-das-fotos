"""Verificador R3v: itens 8 e 11 do revisor R3 (modelo newtoniano + Peters, pn_excentrico.py).

 (11a) convergencia em dt das memorias de pn_excentrico (soma do codigo e trapezio), e0 = 0 e 0.3
 (11b) as mesmas memorias com I_ij'' e I_ij''' ANALITICOS da orbita kepleriana osculante (a, e, anomalia do codigo),
       integradas pelo trapezio: limite adiabatico, sem diferencas finitas
 (11c) correcao nao adiabatica (termos em adot) da energia irradiada numa inspiral circular de Peters, com
       derivadas exatas (sympy): explica o limite dt -> 0 do codigo diferente de Favata LO?
 (8)   peso ABSOLUTO do modo (2,0) oscilatorio nas memorias de janela (para comparar com a memoria de janela com fusao)
Unidades G = c = M = 1. Sistema: M = 65, q = 1.2, 10 Hz (o do exp10/exp12).
Saida: resultados/revisao/rev_R3v_pn.txt
"""
import os
import sys
import time

import numpy as np
import sympy as sp

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import pn_excentrico as PE                              # noqa: E402
import binarias as B                                    # noqa: E402
from memorias import CalculadoraMemoria                 # noqa: E402
from deteccao import MSUN_S                             # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao")
linhas = []
L3 = [(2, 2), (2, -2), (2, 0)]
L2 = [(2, 2), (2, -2)]
CALC = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def calc(L):
    k = tuple(L)
    if k not in CALC:
        CALC[k] = CalculadoraMemoria(L)
    return CALC[k]


def memorias(H, Hd, dt, L, trapezio=False):
    """Energia, desl20 e spin30 (Im) de janela com pesos de soma simples (como o codigo) ou trapezio."""
    w = np.ones(H.shape[0])
    if trapezio:
        w[0] = w[-1] = 0.5
    Bm = (Hd.T * w) @ Hd.conj() * dt
    Am = (H.T * w) @ Hd.conj() * dt
    m = calc(L).memorias_gram(Bm, Am)
    return np.array([m["energia_total"], m["deslocamento"][(2, 0)].real, m["spin"][(3, 0)].imag])


def modos_codigo(eta, e0, f0, dt, L):
    t, h, r, a, e = PE.modos(eta, e0, f0, dt=dt)
    dtt = t[1] - t[0]
    H = np.stack([h[k] for k in L], axis=1)
    return H, B.derivada4(H, dtt), dtt


def modos_analiticos(eta, e0, f0, dt, L):
    """Modos l = 2 com I'' e I''' analiticos da orbita kepleriana osculante (adiabatico)."""
    t, r, v, a, e = PE.orbita(eta, e0, f0, dt)
    dtt = t[1] - t[0]
    p = a * (1 - e ** 2)
    rd = np.sqrt(1 / p) * e * np.sin(v)
    rvd = np.sqrt(1 / p) * (1 + e * np.cos(v))
    c, s = np.cos(v), np.sin(v)
    z = np.zeros_like(r)
    X = np.stack([r * c, r * s, z], axis=1)
    V = np.stack([rd * c - rvd * s, rd * s + rvd * c, z], axis=1)
    Acc = -X / r[:, None] ** 3
    J = -V / r[:, None] ** 3 + 3 * X * (rd / r ** 4)[:, None]
    I2 = eta * (2 * V[:, :, None] * V[:, None, :] + X[:, :, None] * Acc[:, None, :] + Acc[:, :, None] * X[:, None, :])
    I3 = eta * (3 * (Acc[:, :, None] * V[:, None, :] + V[:, :, None] * Acc[:, None, :])
                + X[:, :, None] * J[:, None, :] + J[:, :, None] * X[:, None, :])
    P = PE._projetores()
    H = np.stack([2 * np.einsum("tij,ij->t", I2, P[k]) for k in L], axis=1)
    Hd = np.stack([2 * np.einsum("tij,ij->t", I3, P[k]) for k in L], axis=1)
    return H, Hd, dtt


def favata_lo(x, eta):
    return 8 * np.sqrt(np.pi / 5) * eta * x * 5 / (14 * np.sqrt(6))


if __name__ == "__main__":
    t00 = time.time()
    M, q = 65.0, 1.2
    eta = q / (1 + q) ** 2
    f0 = M * MSUN_S * 10.0
    x0 = (np.pi * f0) ** (2 / 3)
    xf = 1 / 6
    log("M = 65, q = 1.2, 10 Hz: eta = %.5f, x0 = %.5f" % (eta, x0))
    ref_desl = favata_lo(xf, eta) - favata_lo(x0, eta)
    ref_E = 0.5 * eta * (xf - x0)
    log("(11a/11b) valores de janela: energia/[eta(xf-x0)/2], desl20/[Favata LO(xf) - LO(x0)], spin30 (Im)")
    res = {}
    for e0 in (0.0, 0.3):
        for nome, fun, trap in (("codigo, soma", modos_codigo, False), ("codigo, trapezio", modos_codigo, True),
                                ("analitico, trapezio", modos_analiticos, True)):
            vals = []
            for dt in (0.5, 0.25, 0.125, 0.0625):
                H, Hd, dtt = fun(eta, e0, f0, dt, L3)
                vals.append(memorias(H, Hd, dtt, L3, trapezio=trap))
                del H, Hd
            vals = np.array(vals)
            res[(e0, nome)] = vals
            d = np.diff(vals, axis=0) / np.abs(vals[:-1])
            rich = 2 * vals[-1] - vals[-2]                  # Richardson de 1a ordem
            rich2 = (4 * vals[-1] - vals[-2]) / 3            # Richardson de 2a ordem
            log("  e0 = %.1f %-20s E/ref: %s" % (e0, nome, " ".join("%.6f" % (v / ref_E) for v in vals[:, 0])))
            log("        desl20/ref: %s ; spin30: %s" % (" ".join("%.6f" % (v / ref_desl) for v in vals[:, 1]),
                                                     " ".join("%.6f" % v for v in vals[:, 2])))
            log("        v(dt/2)-v(dt) rel. (desl20): %s ; (spin30): %s ; Richardson 1a ordem desl20/ref = %.6f, 2a = %.6f"
                % (" ".join("%+.2e" % x for x in d[:, 1]), " ".join("%+.2e" % x for x in d[:, 2]),
                   rich[1] / ref_desl, rich2[1] / ref_desl))
        log("  (%.0f s)" % (time.time() - t00))
    for nome in ("codigo, soma", "analitico, trapezio"):
        a0, a3 = res[(0.0, nome)], res[(0.3, nome)]
        r = (a3 / a0)
        log("  razao e0=0.3 / e0=0 (%s) em dt = 0.5..0.0625: desl20 %s ; spin30 %s"
            % (nome, " ".join("%.6f" % x for x in r[:, 1]), " ".join("%.6f" % x for x in r[:, 2])))

    # (11c) correcao nao adiabatica, orbita circular de Peters, derivadas exatas
    a, et = sp.symbols("a eta", positive=True)
    Om = a ** sp.Rational(-3, 2)
    f = -sp.Rational(64, 5) * et * a ** -3

    def D(G):
        return sp.diff(G, a) * f - 2 * sp.I * Om * G
    w3 = sp.expand(D(D(D(a ** 2))))
    R = sp.simplify(sp.expand(w3 * sp.conjugate(w3)) / (64 * Om ** 6 * a ** 4))
    Rf = sp.lambdify((a, et), R, "numpy")
    aa = np.linspace(6.0, 1 / x0, 200001)
    dE = 1 / aa ** 2                                       # dE/da da energia de ligacao (a menos de eta/2)
    corr = np.trapezoid((Rf(aa, eta) - 1) * dE, aa) / np.trapezoid(dE, aa)
    log()
    log("(11c) |d^3(r^2 e^{-2i phi})/dt^3|^2 / adiabatico = %s" % sp.series(R, et, 0, 3).removeO())
    log("      correcao relativa nao adiabatica da energia de janela (circular, x0 -> 1/6): %.2e ; em a = 6: %.2e"
        % (corr, Rf(6.0, eta) - 1))

    # (8) peso absoluto do (2,0)
    log()
    log("(8) modo (2,0) oscilatorio (analitico, dt = 0.25): valores ABSOLUTOS de janela (unidades de M)")
    for e0 in (0.1, 0.2, 0.3):
        H, Hd, dtt = modos_analiticos(eta, e0, f0, 0.25, L3)
        v3 = memorias(H, Hd, dtt, L3, trapezio=True)
        v2 = memorias(H[:, :2], Hd[:, :2], dtt, L2, trapezio=True)
        log("  e0 = %.1f: E_janela = %.6e, E(2,0) = %.3e ; desl20 = %.6e, desl20(sem) - desl20(com) = %+.3e (rel. %+.2e)"
            % (e0, v3[0], v3[0] - v2[0], v3[1], v2[1] - v3[1], (v2[1] - v3[1]) / v3[1]))
        del H, Hd
    log("  (%.0f s)" % (time.time() - t00))
    with open(os.path.join(SAIDA, "rev_R3v_pn.txt"), "w") as fo:
        fo.write("\n".join(linhas) + "\n")
