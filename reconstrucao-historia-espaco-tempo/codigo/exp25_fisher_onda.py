"""Experimento 25 (L05): Fisher da onda oscilatoria, da onda completa e da memoria sozinha, sistema A.

Mesma maquinaria do exp24 (espectro exato na rede adimensional, derivada em ln M pela lei de escala, diferencas
finitas com Richardson em q, chi1, chi2 com M fixo). Onda oscilatoria: modos m != 0 do NRHybSur3dq8_CCE
(lista_osc), gerados desde 0.6 f0 (FRAC_INICIO = 0.6), fase orbital zerada em 10 Hz, janela de Tukey ancorada no
instante em que f22 = 0.65 x 10 Hz. Detector: s = Re[exp(2 i psi) sum h_lm Y_lm(iota, phi)].
Parametros: (ln M, q, chi1, chi2, ln D, cos iota, t0, psi, phi).
Casos: osc; osc + memoria nula ("completa"); osc + modos m = 0 do substituto (RN, inclui o toque quase normal);
memoria nula sozinha (phi nao entra). Detector unico (psi = 0 e psi = pi/8) e rede (+ e x).
Saidas: resultados/exp25_fisher_onda.txt e .json
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp24_comum as C                                   # noqa: E402
import observaveis as O                                   # noqa: E402
import binarias as B                                      # noqa: E402
from deteccao import MSUN_S, MPC_S                        # noqa: E402
from harmonicos import sYlm                               # noqa: E402

T0 = time.time()
LINHAS = []
NOMES = ["lnM", "q", "c1", "c2", "lnD", "cosi", "t0", "psi", "phi"]
INTR = ["lnM", "q", "c1", "c2"]
N = 2 ** 19
FMAX = 0.6
T_TAP_OSC = 6250.0
FRAC_JANELA = 0.65


def log(s=""):
    print(s, flush=True)
    LINHAS.append(s)


class EspectroOnda:
    """Espectros adimensionais dos canais Re/Im de cada modo oscilatorio (e da memoria nula e RN) na mesma grade."""

    def __init__(self, q, c1, c2, M, f_ini=10.0, frac_jan=FRAC_JANELA, T_tap=T_TAP_OSC):
        O.FRAC_INICIO = 0.6
        try:
            t, h, ti = O.gerar_janela(q, c1, c2, M, f_ini)
        finally:
            O.FRAC_INICIO = 0.9
        f0 = M * MSUN_S * f_ini
        ta, _, _ = O.instante_frequencia(t, h[(2, 2)], frac_jan * f0)
        self.modos = B.lista_osc()
        k = int(np.searchsorted(t, ta)) - 1
        tt = t[k:]
        W = C.taper(tt - ta, T_tap)
        X = []
        for lm in self.modos:
            z = h[lm][k:] * W
            X += [z.real, z.imag]
        X = np.stack(X, axis=1)
        nmax = int(FMAX * N * C.DT) + 1
        self.F, S, Sp = C.espectro_degrau(tt, X, N, nmax)
        self.R, self.I = S[:, 0::2], S[:, 1::2]
        self.DR, self.DI = Sp[:, 0::2], Sp[:, 1::2]
        del X, S, Sp
        # modos m = 0 do substituto (RN), menos o valor em ta, mesma janela
        Xr = []
        for L in (2, 3, 4):
            z = (h[(L, 0)][k:] - O._interp_em(t, h[(L, 0)], ta)) * W
            Xr += [z.real, z.imag]
        Xr = np.stack(Xr, axis=1)
        _, S, Sp = C.espectro_degrau(tt, Xr, N, nmax)
        self.Rr, self.Ir, self.DRr, self.DIr = S[:, 0::2], S[:, 1::2], Sp[:, 0::2], Sp[:, 1::2]
        # memoria nula (desde 10 Hz, como no exp24), mesma grade
        self.mem = C.EspectroMemoria(q, c1, c2, M, f_ini, N=N, Fmax=FMAX, t=t, h=h, t_i=ti)
        del t, h


def coef(modos, iota, phi, psi):
    return np.array([np.exp(2j * psi) * complex(sYlm(-2, l, m, iota, phi)) for (l, m) in modos])


def proj_osc(E, iota, phi, psi, deriv=False):
    c = coef(E.modos, iota, phi, psi)
    if deriv:
        return E.DR @ c.real - E.DI @ c.imag
    return E.R @ c.real - E.I @ c.imag


def proj_rn(E, iota, psi, deriv=False):
    c = coef([(2, 0), (3, 0), (4, 0)], iota, 0.0, psi)
    if deriv:
        return E.DRr @ c.real - E.DIr @ c.imag
    return E.Rr @ c.real - E.Ir @ c.imag


def proj_mem(E, iota, psi, deriv=False):
    Y = C._Ylist(iota)
    m = E.mem
    if deriv:
        return np.cos(2 * psi) * (m.Dp_ @ Y) + np.sin(2 * psi) * (m.Dx_ @ Y)
    return np.cos(2 * psi) * (m.Sp_ @ Y) + np.sin(2 * psi) * (m.Sx_ @ Y)


def projecao(E, caso, iota, phi, psi, deriv=False):
    if caso == "osc":
        return proj_osc(E, iota, phi, psi, deriv)
    if caso == "completa":
        return proj_osc(E, iota, phi, psi, deriv) + proj_mem(E, iota, psi, deriv)
    if caso == "osc+rn":
        return proj_osc(E, iota, phi, psi, deriv) + proj_rn(E, iota, psi, deriv)
    if caso == "memoria":
        return proj_mem(E, iota, psi, deriv)
    raise ValueError(caso)


def derivadas(E0, Efd, passos, caso, M, D, iota, phi, psi):
    Ms, Ds = M * MSUN_S, D * MPC_S
    k = Ms * Ms / Ds
    f = E0.F / Ms
    s = k * projecao(E0, caso, iota, phi, psi)
    d = {}
    d["lnM"] = k * (2 * projecao(E0, caso, iota, phi, psi) + E0.F * projecao(E0, caso, iota, phi, psi, deriv=True))
    for n in ("q", "c1", "c2"):
        r = []
        for (Em, Ep), hh in zip(Efd[n], passos):
            r.append(k * (projecao(Ep, caso, iota, phi, psi) - projecao(Em, caso, iota, phi, psi)) / (2 * hh))
        d[n] = (4 * r[1] - r[0]) / 3 if len(r) == 2 else r[0]          # Richardson (passos h e h/2)
    d["lnD"] = -s
    eps = 1e-6
    ci = np.cos(iota)
    ip, im = np.arccos(ci + eps), np.arccos(ci - eps)
    d["cosi"] = k * (projecao(E0, caso, ip, phi, psi) - projecao(E0, caso, im, phi, psi)) / (2 * eps)
    d["t0"] = -2j * np.pi * f * s
    d["psi"] = k * (projecao(E0, caso, iota, phi, psi + 1e-6) - projecao(E0, caso, iota, phi, psi - 1e-6)) / 2e-6
    d["phi"] = k * (projecao(E0, caso, iota, phi + 1e-6, psi) - projecao(E0, caso, iota, phi - 1e-6, psi)) / 2e-6
    return s, d, f


def main():
    A = dict(C.SIST_A)
    M, D, iota = A["M"], A["D"], A["iota"]
    phi = 0.0
    log("Experimento 25: Fisher da onda oscilatoria, da completa e da memoria nula (sistema A, phi = 0).")
    t1 = time.time()
    E0 = EspectroOnda(A["q"], A["c1"], A["c2"], M)
    log("espectros centrais: %.1f s" % (time.time() - t1))
    passos = (2e-3, 1e-3)
    Efd = {}
    for n in ("q", "c1", "c2"):
        Efd[n] = []
        for hh in passos:
            par = []
            for sgn in (-1, 1):
                p = dict(q=A["q"], c1=A["c1"], c2=A["c2"])
                p[n] += sgn * hh
                par.append(EspectroOnda(p["q"], p["c1"], p["c2"], M))
            Efd[n].append(tuple(par))
    log("espectros para diferencas finitas: %.0f s" % (time.time() - t1))

    # teste da janela da onda oscilatoria: outra janela (T_tap dobrado, inicio em 0.62 f0)
    Ealt = EspectroOnda(A["q"], A["c1"], A["c2"], M, frac_jan=0.62, T_tap=2 * T_TAP_OSC)
    Ms, Ds = M * MSUN_S, D * MPC_S
    f = E0.F / Ms
    df = f[1] - f[0]
    so = (Ms * Ms / Ds) * proj_osc(E0, iota, phi, 0.0)
    sa = (Ms * Ms / Ds) * proj_osc(Ealt, iota, phi, 0.0)
    for nome in C.PSDS:
        w = C.psd_grade(nome, len(f), df)
        log("  janela da onda (0.65 f0, %d M) contra (0.62 f0, %d M): |ds|/|s| = %.1e (%s, rho_osc = %.1f)"
            % (T_TAP_OSC, 2 * T_TAP_OSC, np.sqrt(C.produto(so - sa, so - sa, w, df) / C.produto(so, so, w, df)), nome,
               np.sqrt(C.produto(so, so, w, df))))
    del Ealt
    # convergencia das diferencas finitas (osc, CE)
    w = C.psd_grade("CE", len(f), df)
    Gh = []
    for j in range(2):
        Efd1 = {n: [Efd[n][j]] for n in Efd}
        _, dd, _ = derivadas(E0, Efd1, (passos[j],), "osc", M, D, iota, phi, 0.0)
        Gh.append(C.matriz_produtos([dd[n] for n in NOMES], w, df))
    _, dR, _ = derivadas(E0, Efd, passos, "osc", M, D, iota, phi, 0.0)
    GR = C.matriz_produtos([dR[n] for n in NOMES], w, df)
    na = np.sqrt(np.outer(np.diag(GR), np.diag(GR)))
    log("  convergencia (osc, CE): max|G(2e-3) - G(1e-3)|/sqrt(GiiGjj) = %.1e ; Richardson contra 1e-3: %.1e"
        % (np.max(np.abs(Gh[0] - Gh[1]) / na), np.max(np.abs(GR - Gh[1]) / na)))
    sp = np.array([C.SIG_PRIOR[n] for n in NOMES])
    l1 = np.linalg.eigvalsh(Gh[1] * np.outer(sp, sp))
    lR = np.linalg.eigvalsh(GR * np.outer(sp, sp))
    log("  autovalores branqueados (osc, CE), h=1e-3 / Richardson - 1: " + " ".join("%+.1e" % x for x in l1 / lR - 1))

    res = {"nomes": NOMES}
    for caso in ("memoria", "osc", "completa", "osc+rn"):
        nomes = [n for n in NOMES if not (caso == "memoria" and n == "phi")]
        log("")
        log("CASO %s (parametros: %s)" % (caso, ", ".join(nomes)))
        res[caso] = {}
        for psi in (0.0, np.pi / 8):
            s1, d1, _ = derivadas(E0, Efd, passos, caso, M, D, iota, phi, psi)
            s2, d2, _ = derivadas(E0, Efd, passos, caso, M, D, iota, phi, psi + np.pi / 4)
            for nome in C.PSDS:
                w = C.psd_grade(nome, len(f), df)
                G1 = C.matriz_produtos([d1[n] for n in nomes], w, df)
                G2 = C.matriz_produtos([d2[n] for n in nomes], w, df)
                rho = np.sqrt(C.produto(s1, s1, w, df))
                for rot, G in (("unico", G1), ("rede", G1 + G2)):
                    if rot == "rede" and psi != 0.0:
                        continue
                    an = C.analise_fisher(G, nomes, C.SIG_PRIOR, intrinsecos=INTR)
                    chave = "%s_psi%.3f_%s" % (rot, psi, nome)
                    res[caso][chave] = dict(rho=rho, lam=an["lam"].tolist(), d_ef=an["d_ef"], mi=an["mi"],
                                            mi_intr=an["mi_intr"], post=an["post"].tolist(), cr=an["cr"].tolist(),
                                            mi_par=an["mi_par"].tolist(), G=G.tolist(), nomes=nomes)
                    log("  %-5s %-5s psi=%.3f rho=%7.2f d_ef=%.2f I=%.1f bits I_intr=%.2f bits | lam: %s"
                        % (nome, rot, psi, rho, an["d_ef"], an["mi"], an["mi_intr"],
                           " ".join("%.2g" % x for x in an["lam"])))
                    log("        post: " + " ".join("%s %.3g" % (n, v) for n, v in zip(nomes, an["post"]))
                        + " | CR: " + " ".join("%s %.3g" % (n, v) for n, v in zip(nomes, an["cr"])))
    # ganho da memoria sobre a onda oscilatoria (distancia-inclinacao)
    log("")
    log("Ganho da memoria (completa contra osc), detector unico psi = 0, sigma sem prior (CR) de ln D e cos iota:")
    for nome in C.PSDS:
        a = res["osc"]["unico_psi0.000_%s" % nome]
        b = res["completa"]["unico_psi0.000_%s" % nome]
        c = res["osc+rn"]["unico_psi0.000_%s" % nome]
        i_d, i_c = NOMES.index("lnD"), NOMES.index("cosi")
        log("  %-5s: CR(lnD) osc %.4g -> completa %.4g -> osc+RN %.4g ; CR(cos i) %.4g -> %.4g -> %.4g ; "
            "I osc %.2f, completa %.2f bits"
            % (nome, a["cr"][i_d], b["cr"][i_d], c["cr"][i_d], a["cr"][i_c], b["cr"][i_c], c["cr"][i_c], a["mi"], b["mi"]))
    log("tempo total %.0f s" % (time.time() - T0))
    with open(os.path.join(C.RES, "exp25_fisher_onda.json"), "w") as fh:
        json.dump(res, fh, default=float)
    with open(os.path.join(C.RES, "exp25_fisher_onda.txt"), "w") as fh:
        fh.write("\n".join(LINHAS) + "\n")


if __name__ == "__main__":
    main()
