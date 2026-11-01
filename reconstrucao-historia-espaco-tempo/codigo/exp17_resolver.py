"""Resolvedor exato das equacoes de memoria no observador (L01/L02, agente D1).

Dado o alvo (quatro memorias fisicas de A num observador) e (q_B, chi2_B, phi'_B) fixos, acha (iota_B, chi1_B, M_B)
com D_B eliminado pela equacao do deslocamento (D_B = desl_B(D = 1 Mpc) / desl_A), como no exp07, mas com os
observaveis corrigidos: deslocamento de JANELA, M_f com E_lig 3PN+SO, quadratura suave (observaveis.py) e,
no conjunto T, todos os multipolos (l <= 8) com o azimute phi'_B medido da fase orbital no pico.
Residuos: (spin, CM, giro) relativos ao alvo. Jacobiano por diferencas centrais: iota 1e-6 rad (so projecao),
chi1 1e-4 (duas ondas), ln M 1e-4 (tres janelas da mesma onda).
"""
import numpy as np
from scipy.optimize import least_squares

import exp17_comum as C

TIPOS = C.TIPOS
LIM = dict(iota=(0.02, np.pi - 0.02), chi1=(-0.8, 0.8), M=(35.0, 250.0))


class Resolvedor:
    def __init__(self, alvo, qB, c2B, conj="T0", phiB=0.0):
        self.alvo = np.array([alvo[k] for k in TIPOS])
        self.qB, self.c2B, self.conj, self.phiB = qB, c2B, conj, phiB
        self.cache = {}
        self.n_ondas = 0

    def mems(self, c1, Ms):
        chave = (round(c1, 14), tuple(round(M, 12) for M in Ms))
        if chave not in self.cache:
            if len(self.cache) > 40:
                self.cache.clear()
            res = C.memorias_varias(self.qB, c1, self.c2B, list(Ms))
            self.n_ondas += 1
            out = []
            for r in res:
                m = r["mem_pico"] if self.conj == "T" else C.so_m0(r["mem_pico"])
                out.append((m, r["aux"]))
            self.cache[chave] = out
        return self.cache[chave]

    def valores(self, iota, mem, M):
        v1 = C.vetor_fisico(mem, iota, self.phiB, M, 1.0)
        DB = v1[0] / self.alvo[0]
        v = v1 / np.array([DB, DB, DB, DB ** 2])
        return v, DB

    def residuo_de(self, iota, mem, M):
        v, _ = self.valores(iota, mem, M)
        return (v[1:] - self.alvo[1:]) / np.abs(self.alvo[1:])

    def residuo(self, x):
        iota, c1, M = x
        (mem, _), = self.mems(c1, (M,))
        return self.residuo_de(iota, mem, M)

    def jac(self, x):
        iota, c1, M = x
        h = 1e-4
        Ms = (M * np.exp(-h), M, M * np.exp(h))
        trio = self.mems(c1, Ms)
        mem0 = trio[1][0]
        e = 1e-6
        Ji = (self.residuo_de(iota + e, mem0, M) - self.residuo_de(iota - e, mem0, M)) / (2 * e)
        JM = (self.residuo_de(iota, trio[2][0], Ms[2]) - self.residuo_de(iota, trio[0][0], Ms[0])) / (2 * h * M)
        hc = 1e-4
        mp = self.mems(c1 + hc, (M,))[0][0]
        mm = self.mems(c1 - hc, (M,))[0][0]
        Jc = (self.residuo_de(iota, mp, M) - self.residuo_de(iota, mm, M)) / (2 * hc)
        # garante o residuo do centro no cache de (c1, (M,))
        self.cache[(round(c1, 14), (round(M, 12),))] = [trio[1]]
        return np.array([Ji, Jc, JM]).T

    def resolver(self, x0, max_nfev=40):
        lo = [LIM["iota"][0], LIM["chi1"][0], LIM["M"][0]]
        hi = [LIM["iota"][1], LIM["chi1"][1], LIM["M"][1]]
        x0 = np.clip(np.array(x0, dtype=float), np.array(lo) + 1e-9, np.array(hi) - 1e-9)
        r = least_squares(self.residuo, x0, jac=self.jac, bounds=(lo, hi), x_scale=[0.1, 0.1, 10.0],
                          xtol=1e-14, ftol=1e-15, gtol=1e-15, max_nfev=max_nfev)
        iota, c1, M = r.x
        (mem, aux), = self.mems(c1, (M,))
        v, DB = self.valores(iota, mem, M)
        return dict(iota=float(iota), chi1=float(c1), M=float(M), D=float(DB), qB=self.qB, c2B=self.c2B,
                    phiB=self.phiB, res=float(np.max(np.abs(self.residuo_de(iota, mem, M)))),
                    dif=((v - self.alvo) / np.abs(self.alvo)).tolist(), M_f=aux["M_f"], E_janela=aux["E_janela"],
                    E_lig=aux["E_lig"], Phi_pico=aux["Phi_pico"], nfev=int(r.nfev), ondas=self.n_ondas,
                    no_limite=bool(np.any(np.isclose(r.x, lo, atol=1e-6)) or np.any(np.isclose(r.x, hi, atol=1e-6))))


def alvo_de(q, c1, c2, M, D, iota, phi=0.0, conj="T0"):
    """Quatro memorias fisicas (dict) de um sistema no observador; e os auxiliares."""
    r = C.memorias_varias(q, c1, c2, [M])[0]
    mem = r["mem_pico"] if conj == "T" else C.so_m0(r["mem_pico"])
    return C.fisicos(mem, iota, phi, M, D), r["aux"]
