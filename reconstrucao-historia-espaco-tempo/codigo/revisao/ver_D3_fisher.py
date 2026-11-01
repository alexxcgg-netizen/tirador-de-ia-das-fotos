"""Verificacao D3: Fisher da memoria nula de A por pipeline independente (ver_D3_comum), dois conjuntos de passos.

Confere: rho_+, rho_x, autovalores branqueados, d_ef, I, I_intr, sigma posterior (exp24_fisher_memoria.txt).
Tambem: sensibilidade aos priors (t0, ln M) e informacao intrinseca.
Uso: python revisao/ver_D3_fisher.py  -> resultados/ver_D3_fisher.json
"""
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, ".."))

A = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, D=400.0, iota=np.radians(50.0))
DCOS = 0.01
FMAX = 1000.0
PSDS = ("aLIGO", "A+", "ET", "CE")


def tarefa(args):
    import ver_D3_comum as V
    rot, q, c1, c2, M, iotas = args
    out = []
    for ts, hp, hx in V.serie(q, c1, c2, M, iotas):
        f, Sp = V.espectro(V.grade(ts, hp))
        _, Sx = V.espectro(V.grade(ts, hx))
        sel = f <= FMAX
        out.append((Sp[sel], Sx[sel]))
    return rot, out, f[sel]


def main():
    import ver_D3_comum as V
    t0 = time.time()
    io = A["iota"]
    c = np.cos(io)
    iotas3 = [io, np.arccos(c + DCOS), np.arccos(c - DCOS)]
    passos = {1: dict(lnM=0.01, q=0.01, c1=0.01, c2=0.01), 2: dict(lnM=0.03, q=0.02, c1=0.02, c2=0.02)}
    tarefas = [("base", A["q"], A["c1"], A["c2"], A["M"], iotas3)]
    for k, P in passos.items():
        for nome, h in P.items():
            for sg in (-1, 1):
                p = dict(q=A["q"], c1=A["c1"], c2=A["c2"], M=A["M"])
                if nome == "lnM":
                    p["M"] = A["M"] * np.exp(sg * h)
                else:
                    p[nome] += sg * h
                tarefas.append(("%d_%s_%d" % (k, nome, sg), p["q"], p["c1"], p["c2"], p["M"], [io]))
    ctx = mp.get_context("spawn")
    with ctx.Pool(2) as pool:
        R = {}
        for rot, out, f in pool.imap_unordered(tarefa, tarefas):
            R[rot] = out
            print(rot, "%.0f s" % (time.time() - t0), flush=True)
    df = f[1] - f[0]
    sp0, sx0 = R["base"][0]
    res = dict(tempo=None, passos=passos)
    W = {p: V.pesos(p, f) for p in PSDS}
    for p in PSDS:
        res.setdefault("rho", {})[p] = (np.sqrt(V.prod(sp0, sp0, W[p], df)), np.sqrt(V.prod(sx0, sx0, W[p], df)))
    print("rho_+, rho_x:", res["rho"])
    nomes = ["lnM", "q", "c1", "c2", "lnD", "cosi", "t0", "psi"]
    dcos_p = (R["base"][1][0] - R["base"][2][0]) / (2 * DCOS)
    for k, P in passos.items():
        d = {}
        for nome, h in P.items():
            d[nome] = (R["%d_%s_1" % (k, nome)][0][0] - R["%d_%s_-1" % (k, nome)][0][0]) / (2 * h)
        d["lnD"] = -sp0
        d["cosi"] = dcos_p
        d["t0"] = -2j * np.pi * f * sp0
        d["psi"] = 2 * sx0
        for p in PSDS:
            Dm = np.array([d[n] for n in nomes])
            G = 4 * df * np.real((Dm * W[p][None, :]) @ Dm.conj().T)
            G = 0.5 * (G + G.T)
            an = V.analise(G, nomes, V.SIG_PRIOR)
            ent = dict(lam=an["lam"].tolist(), d_ef=an["d_ef"], I=an["I"], I_intr=an["I_intr"],
                       post=dict(zip(nomes, an["post"].tolist())),
                       V3=[dict(zip(nomes, np.round(an["V"][:, j], 3).tolist())) for j in range(4)])
            # sensibilidade ao prior
            sens = {}
            for rot, mod in (("t0_10ms", dict(t0=0.01)), ("t0_1s", dict(t0=1.0)), ("M_fator2", dict(lnM=np.log(2) / np.sqrt(12))),
                             ("M_fator10", dict(lnM=np.log(10) / np.sqrt(12))), ("q_1a8", dict(q=7 / np.sqrt(12)))):
                sg = dict(V.SIG_PRIOR)
                sg.update(mod)
                a2 = V.analise(G, nomes, sg)
                sens[rot] = dict(d_ef=a2["d_ef"], I=a2["I"], I_intr=a2["I_intr"], lam=a2["lam"][:4].tolist(),
                                 post_lnM=float(a2["post"][0]))
            ent["sens_prior"] = sens
            res.setdefault("fisher_%d" % k, {})[p] = ent
            print(k, p, "lam", np.array2string(an["lam"][:5], precision=3), "d_ef %.3f I %.2f I_intr %.3f" % (
                an["d_ef"], an["I"], an["I_intr"]), "post lnM %.3f cosi %.3f t0 %.2e" % (
                an["post"][0], an["post"][5], an["post"][6]))
            for rot, s in sens.items():
                print("    prior", rot, "d_ef %.3f I %.2f I_intr %.3f post_lnM %.3f" % (s["d_ef"], s["I"], s["I_intr"], s["post_lnM"]))
            if p == "CE":
                for j in range(4):
                    print("    autovetor", j + 1, {n: v for n, v in ent["V3"][j].items() if abs(v) > 0.1})
    res["tempo"] = time.time() - t0
    with open(os.path.join(AQUI, "..", "..", "resultados", "ver_D3_fisher.json"), "w") as fh:
        json.dump(res, fh, default=float, indent=1)
    print("tempo %.0f s" % res["tempo"])


if __name__ == "__main__":
    main()
