"""Verificacao (R2v), continuacao de rev_R2v_match2.py: o 'ouro' com a convencao de fase do exp07.

O rev_R2v_match2 mostrou que o ouro de rev_R2v_match nao era autoconsistente (A contra A com inicio em 5.0 e
5.3 Hz: 1 - match 2.5e-3). Causa: o gwsurrogate zera a fase orbital em f_ref, que por padrao e f_low; mudar o
inicio gira a binaria em torno de z (h_lm -> h_lm e^{-i m dphi}) e, num observador fixo, muda a mistura dos
modos m != 2. O exp07 usa f_ref = f_low = 10 Hz. Aqui o ouro e refeito com f_ref = 10 Hz (inicio 5 Hz, cosseno
ate 7 Hz, m = 0 com rampa, tempo continuo), e tambem maximizado no azimute phi_B do observador de B (as memorias
m = 0 nao dependem de phi_B: e um parametro livre da familia que o match do 07 nao maximiza).
1) Autoconsistencia: A (inicio 5.0) contra A (inicio 5.3 Hz) com f_ref = 10 Hz.
2) Familia de A (chi2_B = -0.2): ouro (f_ref 10 Hz), ouro maximizado em phi_B, tratamento do R2 e base do exp07.
3) exp13 (q = 1, chi_s = +0.3, d = 0.1, 0.2, 0.3; chi_s = -0.5, d = 0.2) e pares (1, 0), (2, 0) do exp07.
Saida: resultados/revisao/rev_R2v_match3.txt
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize_scalar

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402
import rev_R2v_match as RM                              # noqa: E402
import rev_R2v_match2 as R2M                            # noqa: E402
from harmonicos import sYlm                             # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
FS, DTS = RM.FS, RM.DTS
NMIN = 2 ** 19
MS = (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def gerar_ref(par, f_ini, f_ref=10.0):
    """Modos com inicio em f_ini e fase orbital zerada em f_ref (Hz), grade de 1/4096 s."""
    Ms = par["M"] * Dt.MSUN_S
    t, h, _ = B._sur()(par["q"], [0, 0, par["c1"]], [0, 0, par["c2"]], dt=DTS / Ms, f_low=f_ini * Ms, f_ref=f_ref * Ms)
    return t, {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}


def ouro_m(par, f_ini=5.0, f_tap=7.0):
    """Componentes por m da deformacao no observador (phi = 0), com o tratamento do ouro.
    Devolve dict m -> serie complexa (m != 0, com cosseno) e a parte m = 0 (com rampa)."""
    t, h = gerar_ref(par, f_ini)
    fase = np.unwrap(np.angle(h[(2, 2)]))
    f22 = np.abs(np.gradient(fase, t)) / (2 * np.pi) / (par["M"] * Dt.MSUN_S)
    k = int(np.argmax(f22 > f_tap))
    w = np.ones(len(t))
    w[:k] = 0.5 * (1 - np.cos(np.pi * np.arange(k) / k))
    esc = par["M"] * Dt.MSUN_S / (par["D"] * Dt.MPC_S)
    n_hold, n_rampa = int(4 * FS), int(8 * FS)
    comp = {}
    for m in MS:
        s = sum(h[(l, mm)] * sYlm(-2, l, mm, par["iota"], 0.0) for (l, mm) in B.lista_osc() if mm == m) * esc
        comp[m] = np.concatenate([s * w, np.zeros(n_hold + n_rampa)])
    m0 = sum(h[k_] * sYlm(-2, k_[0], 0, par["iota"], 0.0) for k_ in B.MODOS_M0) * esc
    del t, h
    m0 = (m0 - m0[0]) * w
    rampa = m0[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
    m0 = np.concatenate([m0, np.full(n_hold, m0[-1]), rampa])
    return comp, m0


def serie_phi(comp, m0, phi):
    return sum(comp[m] * np.exp(1j * m * phi) for m in MS) + m0


class Comparador:
    """1 - match de A (fixo) contra B(phi_B), com espectros pre-calculados por m."""

    def __init__(self, a):
        self.n = NMIN
        while self.n < 2 * len(a):
            self.n *= 2
        self.f = np.fft.rfftfreq(self.n, DTS)
        self.df = self.f[1] - self.f[0]
        self.Sn = R2M.psd(len(self.f), self.df, 10.0)
        self.ok = self.f >= 10.0
        self.Af = np.fft.rfft(a.real, self.n) * DTS
        self.aa = 4 * np.sum(np.abs(self.Af[self.ok]) ** 2 / self.Sn[self.ok]) * self.df

    def preparar_B(self, comp, m0):
        self.Fr = {m: np.fft.rfft(comp[m].real, self.n) * DTS for m in MS}
        self.Fi = {m: np.fft.rfft(comp[m].imag, self.n) * DTS for m in MS}
        self.F0 = np.fft.rfft(m0.real, self.n) * DTS

    def um_menos(self, phi):
        Bf = self.F0 + sum(self.Fr[m] * np.cos(m * phi) - self.Fi[m] * np.sin(m * phi) for m in MS)
        bb = 4 * np.sum(np.abs(Bf[self.ok]) ** 2 / self.Sn[self.ok]) * self.df
        W = np.where(self.ok, self.Af * np.conj(Bf) / self.Sn, 0)
        up = 4
        N = self.n * up
        integ = np.zeros(N, dtype=complex)
        integ[:len(self.f)] = W
        serie = np.abs(np.fft.ifft(integ)) * N
        i = int(np.argmax(serie))
        tau0 = (i if i < N // 2 else i - N) * DTS / up
        fk, Wk = self.f[self.ok], W[self.ok]
        r = minimize_scalar(lambda tau: -np.abs(np.sum(Wk * np.exp(2j * np.pi * fk * tau))),
                            bounds=(tau0 - DTS / up, tau0 + DTS / up), method="bounded", options=dict(xatol=1e-6 * DTS))
        return 1 - float(4 * self.df * max(-r.fun, serie[i]) / np.sqrt(self.aa * bb))

    def max_phi(self):
        phis = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        ys = [self.um_menos(p) for p in phis]
        j = int(np.argmin(ys))
        r = minimize_scalar(self.um_menos, bounds=(phis[j] - np.pi / 12, phis[j] + np.pi / 12), method="bounded",
                            options=dict(xatol=1e-5))
        return min(r.fun, ys[j]), float(r.x if r.fun < ys[j] else phis[j])


def r2(par):
    ts, s = RM.exp07_serie(par)
    return RM.tratar(ts, s, taper=0.5, rampa=True)


if __name__ == "__main__":
    t0 = time.time()
    dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
    A, alvo = dados["A"], dados["alvo"]
    cA, mA = ouro_m(A)
    oA = serie_phi(cA, mA, 0.0)
    del cA, mA
    cp = Comparador(oA)
    c2, m2 = ouro_m(A, 5.3)
    cp.preparar_B(c2, m2)
    log("1) Autoconsistencia (f_ref = 10 Hz): A (inicio 5.0 Hz) contra A (inicio 5.3 Hz): 1-match %.2e" % cp.um_menos(0.0))
    del c2, m2
    log("2) Familia de A (chi2_B = -0.2, mesmas 4 memorias no nivel A), aLIGO, f_min = 10 Hz:")
    xA = r2(A)
    sA07 = RM.exp07_serie(A)
    dq, yo, yphi, yr = [], [], [], []
    for qB in (1.15, 1.18, 1.19, 1.195, 1.205, 1.21, 1.25):
        pB, r = E7.resolver(alvo, qB, -0.2, (A["iota"], 0.3, 65.0))
        cB, mB = ouro_m(pB)
        cp.preparar_B(cB, mB)
        del cB, mB
        o = cp.um_menos(0.0)
        ophi, phib = cp.max_phi()
        x = R2M.match(xA, r2(pB), n_min=NMIN)
        tsB, sB = RM.exp07_serie(pB)
        base = 1 - Dt.comparar(sA07[0], sA07[1], tsB, sB, "aLIGO", fmin=10.0)["+"]["match"]
        del tsB, sB
        dq.append(abs(qB - 1.2))
        yo.append(o)
        yphi.append(ophi)
        yr.append(x)
        log("   q_B %.3f (residuo %.1e): ouro %.3e (rho_crit %.1f) | ouro max. em phi_B %.3e (rho_crit %.1f, phi_B %.3f rad) "
            "| R2 %.3e (rho_crit %.1f) | base exp07 %.3e (rho_crit %.1f)"
            % (qB, r, o, 1 / np.sqrt(2 * o), ophi, 1 / np.sqrt(2 * ophi), phib, x, 1 / np.sqrt(2 * x), base,
               1 / np.sqrt(2 * base)))
    dq = np.array(dq)
    for nome, y in (("ouro", yo), ("ouro max. phi_B", yphi), ("R2", yr)):
        y = np.array(y)
        p = np.polyfit(np.log(dq), np.log(y), 1)
        sel = dq <= 0.0101
        p2 = np.polyfit(np.log(dq[sel]), np.log(y[sel]), 1)
        log("   %-16s: 1-match = %.3g dq^%.2f (todos) ; dq <= 0.01: %.3g dq^%.2f -> |dq| nao separado na SNR 66: %.4f ; "
            "SNR 899: %.5f" % (nome, np.exp(p[1]), p[0], np.exp(p2[1]), p2[0],
                               (1 / (2 * 66.0 ** 2) / np.exp(p2[1])) ** (1 / p2[0]),
                               (1 / (2 * 899.0 ** 2) / np.exp(p2[1])) ** (1 / p2[0])))
    log("   (%.0f s)" % (time.time() - t0))
    del xA, sA07
    log("3) exp13 e pares do exp07 com o ouro (f_ref = 10 Hz) e com o tratamento do R2:")
    casos = []
    for chi_s, ds in ((0.3, (0.1, 0.2, 0.3)), (-0.5, (0.1, 0.2))):
        pA = dict(M=65.0, q=1.0, c1=chi_s, c2=chi_s, D=400.0, iota=np.radians(50.0))
        casos.append((pA, [("chi_s %+.1f d %.1f" % (chi_s, d), dict(pA, c1=chi_s + d, c2=chi_s - d)) for d in ds]))
    casos.append((A, [("par (%.0f, %+.1f)" % (p["qB"], p["c2B"]),
                       dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"]))
                      for p in dados["pares"] if (p["qB"], p["c2B"]) in ((1.0, 0.0), (2.0, 0.0))]))
    for pA, lst in casos:
        cA, mA = ouro_m(pA)
        cpA = Comparador(serie_phi(cA, mA, 0.0))
        del cA, mA
        xA = r2(pA)
        for nome, pB in lst:
            cB, mB = ouro_m(pB)
            cpA.preparar_B(cB, mB)
            del cB, mB
            o = cpA.um_menos(0.0)
            ophi, _ = cpA.max_phi()
            x = R2M.match(xA, r2(pB), n_min=NMIN)
            log("   %-18s ouro %.3e (rho_crit %.1f) | ouro max. phi_B %.3e (rho_crit %.1f) | R2 %.3e (rho_crit %.1f)"
                % (nome, o, 1 / np.sqrt(2 * o), ophi, 1 / np.sqrt(2 * ophi), x, 1 / np.sqrt(2 * x)))
        del xA, cpA
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "revisao", "rev_R2v_match3.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
