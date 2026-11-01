"""L03, tarefa 3: a familia (aproximada) de binarias com as mesmas memorias em K janelas. Como encolhe com K?

Alvo: sistema A (exp07). Incognitas de B: (q, chi1, chi2, M, iota, D). Com q_B fixo num perfil, minimiza-se o residuo
relativo r = (y_B - y_A)/|y_A| (todas as janelas e tipos) sobre as outras 5 (Levenberg-Marquardt proprio), partindo
  (i) de A (com q trocado) e por continuacao em q_B a partir de A (varredura para cima e para baixo),
  (ii) dos pares do exp07 (q_B = 1, 2, 3 com chi2_B = 0; resolvidos para UMA janela e o deslocamento total),
  (iii) de partidas aleatorias (semente fixa) em q_B = 1.5 e 3.
Conjuntos: T0 (quatro memorias, m = 0) e O0 (deslocamento e spin, m = 0); nivel A, deslocamento de janela.
Janelas [t_i(f), fim], f geometricas de 10 Hz a f_max = 0.012/(M_A MSUN_S) = 37.5 Hz (e 10 + 20 Hz, como na R4).

Uso: python exp22_familia_K.py CONFIG [CONFIG ...]   (saida resultados/exp22_familia_<CONFIG>.json e .txt)
"""
import json
import os
import sys
import time

import numpy as np

import exp20_comum as C
from deteccao import MSUN_S

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = C.PAR_A
FMAX = 0.012 / (A["M"] * MSUN_S)
CONFIGS = {
    "T0_K1": ("T0", [10.0]),
    "T0_K2r": ("T0", [10.0, 20.0]),
    "T0_K2": ("T0", C.freqs_geom(10.0, FMAX, 2)),
    "T0_K3": ("T0", C.freqs_geom(10.0, FMAX, 3)),
    "T0_K4": ("T0", C.freqs_geom(10.0, FMAX, 4)),
    "O0_K2": ("O0", C.freqs_geom(10.0, FMAX, 2)),
    "O0_K3": ("O0", C.freqs_geom(10.0, FMAX, 3)),
    "O0_K4": ("O0", C.freqs_geom(10.0, FMAX, 4)),
    "O0_K6": ("O0", C.freqs_geom(10.0, FMAX, 6)),
}
TIPOS_CONJ = {"T0": C.TIPOS, "O0": ("deslocamento", "spin")}
QB = [1.0, 1.1, 1.3, 1.6, 2.0, 3.0]
LIM = dict(c1=(-0.8, 0.8), c2=(-0.8, 0.8), M=(40.0, 120.0), iota=(0.05, np.pi / 2 - 0.01), D=(100.0, 1500.0))
LIVRES = ("c1", "c2", "M", "iota", "D")


def y(par, freqs, tipos):
    return C.observaveis_K(par, freqs, tipos=tipos).ravel()


def _y_de_mem(res, iota, D, M, tipos):
    idx = [C.TIPOS.index(t) for t in tipos]
    return np.array([C.no_obs(m, iota, 0.0, M, D)[idx] for m, _ in res]).ravel()


class _Res:
    pass


def resolver(x0, qB, alvo, freqs, tipos, maxit=30):
    """Levenberg-Marquardt proprio nas 5 livres (chi1, chi2, M, iota, D), passos de norma minima (lstsq), jacobiano por
    diferencas centrais (passos 1e-3 em chi, 1e-3 M: acima do piso de ruido do substituto; iota e D sem regerar a onda).
    (scipy least_squares 'trf' com limites estagnava nos problemas subdeterminados: ver o relatorio, secao 6.)"""
    lo = np.array([LIM[n][0] for n in LIVRES])
    hi = np.array([LIM[n][1] for n in LIVRES])
    cache = {}

    def mems(xv):
        k = tuple(np.round(xv[:3], 14))
        if k not in cache:
            if len(cache) > 8:
                cache.clear()
            cache[k] = C.janelas(qB, xv[0], xv[1], xv[2], freqs)
        return cache[k]

    def fun(xv):
        return (_y_de_mem(mems(xv), xv[3], xv[4], xv[2], tipos) - alvo) / np.abs(alvo)

    def jac(xv):
        J = np.zeros((len(alvo), 5))
        for i, hstep in enumerate((1e-3, 1e-3, 1e-3 * xv[2])):
            xp, xm = np.array(xv, float), np.array(xv, float)
            xp[i] += hstep
            xm[i] -= hstep
            J[:, i] = (fun(xp) - fun(xm)) / (2 * hstep)
        res = mems(xv)
        for i, hstep in ((3, 1e-5), (4, 1e-5 * xv[4])):
            xp, xm = np.array(xv, float), np.array(xv, float)
            xp[i] += hstep
            xm[i] -= hstep
            J[:, i] = ((_y_de_mem(res, xp[3], xp[4], xp[2], tipos) - _y_de_mem(res, xm[3], xm[4], xm[2], tipos))
                       / np.abs(alvo)) / (2 * hstep)
        return J

    x = np.clip(np.array([x0[n] for n in LIVRES], float), lo + 1e-6, hi - 1e-6)
    f = fun(x)
    nf = 1
    lam = 1e-8
    it = 0
    for it in range(maxit):
        J = jac(x)
        nf += 6
        Dg = np.linalg.norm(J, axis=0) + 1e-30
        melhorou = False
        for _ in range(12):
            Ja = np.vstack([J, np.sqrt(lam) * np.diag(Dg)])
            fa = np.concatenate([f, np.zeros(5)])
            dx = -np.linalg.lstsq(Ja, fa, rcond=None)[0]
            xn = np.clip(x + dx, lo + 1e-9, hi - 1e-9)
            fn = fun(xn)
            nf += 1
            if np.linalg.norm(fn) < np.linalg.norm(f):
                ganho = 1 - np.linalg.norm(fn) / np.linalg.norm(f)
                x, f = xn, fn
                lam = max(lam / 10, 1e-12)
                melhorou = True
                break
            lam *= 10
        if not melhorou or ganho < 1e-9 or np.max(np.abs(f)) < 1e-12:
            break
    p = dict(q=qB, phi=0.0)
    p.update(dict(zip(LIVRES, x)))
    r = _Res()
    r.fun, r.nfev, r.nit = f, nf, it + 1
    return p, r


def fmt(p):
    return "q %.3f chi1 %+.4f chi2 %+.4f M %.3f iota %.2f D %.1f" % (p["q"], p["c1"], p["c2"], p["M"],
                                                                      np.degrees(p["iota"]), p["D"])


def rodar(nome):
    conj, freqs = CONFIGS[nome]
    tipos = TIPOS_CONJ[conj]
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)

    t0 = time.time()
    alvo = y(A, freqs, tipos)
    log("%s: conjunto %s, janelas desde %s Hz, %d equacoes, 5 incognitas (q_B fixo)"
        % (nome, conj, ", ".join("%.2f" % f for f in freqs), len(alvo)))
    pares = json.load(open(os.path.join(RAIZ, "resultados", "exp07_pares.json")))["pares"]
    P07 = {p["qB"]: dict(q=p["qB"], c1=p["c1"], c2=p["c2B"], M=p["M"], iota=p["iota"], D=p["D"])
           for p in pares if p["c2B"] == 0.0}
    rng = np.random.default_rng(20)
    out = []
    # varredura a partir de A para cima (1.3 -> 3.0) e para baixo (1.1 -> 1.0), continuando da melhor solucao anterior
    for ramo in ([q for q in QB if q > A["q"]], [q for q in sorted(QB, reverse=True) if q < A["q"]]):
        ant = dict(A)
        for qB in ramo:
            partidas = [("A", dict(A, q=qB))]
            if ant is not A:
                partidas.append(("continuacao", dict(ant, q=qB)))
            if qB in P07:
                partidas.append(("exp07", P07[qB]))
            if qB in (1.6, 3.0):
                partidas.append(("aleatoria", dict(q=qB, c1=rng.uniform(-0.7, 0.7), c2=rng.uniform(-0.7, 0.7),
                                                   M=rng.uniform(55, 85), iota=rng.uniform(0.7, 1.05),
                                                   D=rng.uniform(330, 470))))
            melhor = None
            for rot, x0 in partidas:
                p, r = resolver(x0, qB, alvo, freqs, tipos)
                mx = float(np.max(np.abs(r.fun)))
                log("  q_B=%.2f partida %-11s: max|r| %.2e norma %.2e (%3d aval., %2d it.) -> %s"
                    % (qB, rot, mx, np.linalg.norm(r.fun), r.nfev, r.nit, fmt(p)))
                out.append(dict(qB=qB, partida=rot, par=p, res=r.fun.tolist(), maxres=mx,
                                norma=float(np.linalg.norm(r.fun))))
                if melhor is None or np.linalg.norm(r.fun) < melhor[1]:
                    melhor = (p, np.linalg.norm(r.fun), mx)
            ant = melhor[0]
            log("  -> q_B=%.2f melhor: norma %.2e max %.2e" % (qB, melhor[1], melhor[2]))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RAIZ, "resultados", "exp22_familia_%s.json" % nome), "w") as fh:
        json.dump(dict(config=nome, conj=conj, freqs=freqs, solucoes=out), fh, indent=1, default=float)
    with open(os.path.join(RAIZ, "resultados", "exp22_familia_%s.txt" % nome), "w") as fh:
        fh.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        rodar(nome)
