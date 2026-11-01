"""Experimento 17 (L02, tarefa 4): mapa global da fibra F^-1(F(A)) em (q_B, chi2_B), para T0 e T.

A: M 65, q 1.2, chi (0.3, -0.2), D 400 Mpc, iota 50 graus (alvo de exp17_resolver.alvo_de; T com phi'_A = 0).
Para cada (q_B, chi2_B) da grade de exp17_fibra_tabela (q_B 1.0..4.0 passo 0.25; chi2_B -0.8..0.8 passo 0.2):
  1. interpolante dos multipolos: baricentrico em chi1 (13 nos de Chebyshev em [-0.8, 0.8]) x spline cubica em ln M
     (40 nos em [45, 130] M_sol);
  2. busca exaustiva numa grade densa (chi1: 81, M: 121, iota: 179 valores de 1 a 179 graus) do residuo
     ||(spin, CM, giro)_B / alvo - 1|| com D_B eliminado pelo deslocamento; minimos locais com residuo < 0.05;
  3. refinamento no interpolante (least_squares) e agrupamento das solucoes distintas;
  4. polimento com avaliacoes exatas (exp17_resolver.Resolvedor) de cada solucao T0 (e das de T num subconjunto).
T: phi'_B em 8 valores (k pi/4): existencia de solucao para algum phi'_B e a curva (M, chi1, iota, D)(phi'_B).
Restricao de M: a razao CM/(M desl) do observador limita M_B (exp17_interpretacao.txt, item 6; ver exp17_fibra_tabela),
por isso a tabela cobre [45, 130]; minimos na borda de M sao marcados ('borda') para conferir se a faixa basta.
Uso: python exp17_fibra.py DIRETORIO_DA_TABELA [polir=1]
Saidas: resultados/exp17_fibra.txt, resultados/exp17_fibra.json, figuras/e17_fibra.png
"""
import json
import os
import sys
import time

import numpy as np
from scipy.interpolate import BarycentricInterpolator, CubicSpline
from scipy.optimize import least_squares

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402
import exp17_resolver as R                               # noqa: E402
from harmonicos import sYlm                              # noqa: E402
from deteccao import MSUN_S, MPC_S                       # noqa: E402
from exp17_fibra_tabela import QB, C2B                   # noqa: E402

A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0))
TIPOS = C.TIPOS
S_T = {"deslocamento": -2, "spin": -2, "cm": -2, "giroscopica": 0}
PHIS = tuple(np.arange(8) * np.pi / 4)
SAIDA = os.path.join(AQUI, "..", "resultados", "exp17_fibra")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


class Tabela:
    def __init__(self, pasta, qB, c2B, K):
        z = np.load(os.path.join(pasta, "tab_%.2f_%+.2f.npz" % (qB, c2B)))
        self.X, self.aux = z["X"], z["aux"]
        self.chi, self.M = z["chi1"], z["M"]
        self.lnM = np.log(self.M)
        self.K = K
        self.off = {}
        o = 0
        for t in TIPOS:
            self.off[t] = o
            o += len(K[t])
        self.m = np.concatenate([[k[1] for k in K[t]] for t in TIPOS])
        self.qB, self.c2B = qB, c2B
        # splines em ln M (uma por no de chi1) e pesos baricentricos dos nos de chi1
        self.spl = CubicSpline(self.lnM, np.moveaxis(self.X, 1, 0), axis=0)      # (lnM) -> (13, nK)
        x = self.chi
        self.wb = np.array([1.0 / np.prod([x[k] - x[j] for j in range(len(x)) if j != k]) for k in range(len(x))])
        self._Ycache = {}

    def _pesos(self, chi1):
        chi1 = np.atleast_1d(chi1)
        d = chi1[:, None] - self.chi[None, :]
        exato = np.isclose(d, 0.0, atol=1e-14)
        d = np.where(exato, 1.0, d)
        W = self.wb[None, :] / d
        W = W / W.sum(axis=1, keepdims=True)
        lin = exato.any(axis=1)
        W[lin] = exato[lin].astype(float)
        return W

    def interp(self, chi1, M):
        """Multipolos (nK) interpolados em pontos (arrays 1D chi1 e M): devolve (len(chi1), len(M), nK)."""
        Xm = self.spl(np.log(np.atleast_1d(M)))                                   # (nM, 13, nK)
        W = self._pesos(chi1)                                                     # (nchi, 13)
        return np.einsum("ck,mkx->cmx", W, Xm)

    def Y(self, iotas, phi, m0):
        """Matriz (len(iotas), 4, nK) de harmonicos."""
        iotas = np.atleast_1d(iotas)
        if len(iotas) == 1:
            ch = (float(iotas[0]), float(phi), m0)
            if ch not in self._Ycache:
                if len(self._Ycache) > 500:
                    self._Ycache.clear()
                self._Ycache[ch] = self._Y(iotas, phi, m0)
            return self._Ycache[ch]
        return self._Y(iotas, phi, m0)

    def _Y(self, iotas, phi, m0):
        Y = np.zeros((len(iotas), 4, len(self.m)), dtype=complex)
        for i, t in enumerate(TIPOS):
            for j, (l, m) in enumerate(self.K[t]):
                if m0 and m != 0:
                    continue
                Y[:, i, self.off[t] + j] = sYlm(S_T[t], l, m, iotas, phi)
        return Y


def projetar(X, Y):
    """X (..., nK), Y (ni, 4, nK) -> F adimensional (..., ni, 4)."""
    sh = X.shape[:-1]
    zz = (X.reshape(-1, X.shape[-1]) @ Y.reshape(-1, Y.shape[-1]).T).reshape(sh + Y.shape[:2])
    out = zz.real.copy()
    out[..., 1] = -zz[..., 1].imag
    return out


def residuos(F, M, alvo):
    """F adimensional (..., 4) com M (broadcast) -> residuos relativos (spin, CM, giro) com D_B eliminado."""
    Ms = M * MSUN_S
    desl1 = F[..., 0] * Ms / MPC_S                      # desl fisico com D = 1 Mpc
    DB = desl1 / alvo[0]                                # Mpc
    Ds = DB * MPC_S
    spin = F[..., 1] * Ms ** 2 / Ds
    cm = F[..., 2] * Ms ** 2 / Ds
    giro = F[..., 3] * (Ms / Ds) ** 2
    r = np.stack([(spin - alvo[1]) / abs(alvo[1]), (cm - alvo[2]) / abs(alvo[2]), (giro - alvo[3]) / abs(alvo[3])], -1)
    return r, DB


def buscar(tab, alvo, phi, m0):
    chi_d = np.linspace(-0.8, 0.8, 81)
    M_d = np.exp(np.linspace(np.log(45.0), np.log(130.0), 121))
    io_d = np.radians(np.arange(1.0, 179.5, 1.0))
    Xd = tab.interp(chi_d, M_d)                          # (81, 121, nK)
    Y = tab.Y(io_d, phi, m0)
    F = projetar(Xd, Y)                                  # (81, 121, 179, 4)
    r, DB = residuos(F, M_d[None, :, None], alvo)
    nr = np.linalg.norm(r, axis=-1)
    del F, r
    # minimos locais (vizinhanca 3x3x3) abaixo de 0.05
    from scipy.ndimage import minimum_filter
    loc = (nr == minimum_filter(nr, size=3, mode="nearest")) & (nr < 0.05)
    idx = np.argwhere(loc)
    cands = [(chi_d[i], M_d[j], io_d[k], nr[i, j, k]) for i, j, k in idx]
    Ycache = {}

    def f_res(x):
        iota, c1, M = x
        X1 = tab.interp([c1], [M])[0, 0]
        key = round(iota, 15)
        Yi = tab.Y([iota], phi, m0)
        Fi = projetar(X1, Yi)[0]
        rr, _ = residuos(Fi, M, alvo)
        return rr

    sols = []
    escolhidos = []
    for c in sorted(cands, key=lambda c: c[3]):
        if all(abs(c[0] - e[0]) > 0.06 or abs(np.log(c[1] / e[1])) > 0.03 or abs(c[2] - e[2]) > np.radians(3.0)
               for e in escolhidos):
            escolhidos.append(c)
        if len(escolhidos) >= 8:
            break
    for (c1, M, io, n0) in escolhidos:
        try:
            s = least_squares(f_res, [io, c1, M], bounds=([0.01, -0.8, 45.0], [np.pi - 0.01, 0.8, 130.0]),
                              x_scale=[0.1, 0.1, 10.0], xtol=1e-13, ftol=1e-14, gtol=1e-14, diff_step=1e-6)
        except Exception:
            continue
        res = float(np.max(np.abs(s.fun)))
        novo = True
        for so in sols:
            if abs(so["iota"] - s.x[0]) < 1e-3 and abs(so["chi1"] - s.x[1]) < 1e-3 and abs(so["M"] - s.x[2]) < 1e-2:
                novo = False
                break
        if novo:
            X1 = tab.interp([s.x[1]], [s.x[2]])[0, 0]
            Fi = projetar(X1, tab.Y([s.x[0]], phi, m0))[0]
            _, DB = residuos(Fi, s.x[2], alvo)
            sols.append(dict(iota=float(s.x[0]), chi1=float(s.x[1]), M=float(s.x[2]), D=float(np.squeeze(DB)), res_interp=res,
                             n_grade=float(n0)))
    return sols, float(nr.min())


def processar(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    pasta, qB, c2B, K, a0, aT, alvo0, polir = arg
    t0 = time.time()
    tab = Tabela(pasta, qB, c2B, K)
    s0, nmin0 = buscar(tab, a0, 0.0, True)
    reg = dict(qB=float(qB), c2B=float(c2B), T0=s0, nmin_T0=nmin0, T={})
    for phi in PHIS:
        sT, nminT = buscar(tab, aT, phi, False)
        reg["T"]["%.4f" % phi] = sT
    if polir:
        for s in s0:
            if abs(abs(s["chi1"]) - 0.8) < 1e-6 or s["M"] < 45.5 or s["M"] > 129.5 or s["res_interp"] > 1e-3:
                s["borda"] = True                    # minimo na borda do dominio ou residuo grande: nao e solucao
                continue
            rs = R.Resolvedor(alvo0, float(qB), float(c2B), "T0")
            p = rs.resolver((s["iota"], s["chi1"], s["M"]), max_nfev=12)
            s.update(exato=dict(iota=p["iota"], chi1=p["chi1"], M=p["M"], D=p["D"], res=p["res"], M_f=p["M_f"],
                                E_janela=p["E_janela"], E_lig=p["E_lig"], no_limite=p["no_limite"], ondas=p["ondas"]))
    reg["tempo"] = time.time() - t0
    return reg


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    pasta = sys.argv[1]
    polir = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    z = np.load(os.path.join(pasta, "chaves.npz"))
    K = {t: [tuple(int(a) for a in x) for x in z[t]] for t in TIPOS}
    alvo0, auxA = R.alvo_de(A["q"], A["c1"], A["c2"], A["M"], A["D"], A["iota"], 0.0, "T0")
    alvoT, _ = R.alvo_de(A["q"], A["c1"], A["c2"], A["M"], A["D"], A["iota"], 0.0, "T")
    a0 = np.array([alvo0[k] for k in TIPOS])
    aT = np.array([alvoT[k] for k in TIPOS])
    log("Fibra de A (T0: so m = 0; T: todos os m, phi'_A = 0). Alvo T0: %s ; alvo T: %s" % (a0, aT))
    args = [(pasta, qB, c2B, K, a0, aT, alvo0, polir) for qB in QB for c2B in C2B]
    if len(sys.argv) > 3:
        i0, i1 = map(int, sys.argv[3].split(":"))
        args = args[i0:i1]
    with mp.get_context("spawn").Pool(2) as pool:
        regs = pool.map(processar, args, chunksize=1)
    resultado = {}
    for reg in regs:
        s0 = reg["T0"]
        nT = sum(len(v) > 0 for v in reg["T"].values())
        log("q_B %.2f chi2_B %+.2f: T0 %d solucao(oes) %s | T: phi' com solucao %d/8 (max %d por phi') | min grade T0 %.1e (%.0f s)"
            % (reg["qB"], reg["c2B"], len(s0), "; ".join("chi1 %+.4f M %.2f iota %.2f D %.1f res_int %.0e%s" % (
                s["chi1"], s["M"], np.degrees(s["iota"]), s["D"], s["res_interp"],
                (" exato %.0e" % s["exato"]["res"]) if "exato" in s else "") for s in s0),
               nT, max(len(v) for v in reg["T"].values()), reg["nmin_T0"], reg["tempo"]))
        resultado["%.2f|%+.2f" % (reg["qB"], reg["c2B"])] = reg
    sufixo = "" if len(sys.argv) <= 3 else "_" + sys.argv[3].replace(":", "_")
    with open(SAIDA + sufixo + ".json", "w") as fh:
        json.dump(dict(alvo_T0=a0.tolist(), alvo_T=aT.tolist(), pontos=resultado), fh, indent=0)
    with open(SAIDA + sufixo + ".txt", "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    log("(%.0f s)" % (time.time() - t0))
