"""Verificacao D8 (L16, exp40_pares): os residuos dos pares re-solvidos (1.5e-6, 9.5e-7, ...) estao acima ou abaixo
do tremor do SEOBNRv5EHM? Avalia max|dif| no ponto re-solvido e com perturbacoes de 1e-10, 1e-8 e 1e-6 (relativas)
em M e em chi1 e com l0 = 1e-6 (todas inobservaveis), para dois pares. Alvo A com as correcoes (janela de 10 Hz)."""
import json
import os
import sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import exp40_comum as C


def dif(par, l0, alvo):
    res, _ = C.avaliar(par["q"], par["c1"], par["c2"], par["M"], par["e"], l0, freqs=(10.0,))
    v = C.fisicos(res[0]["com"][0], par["iota"], par["M"], par["D"])
    d = C.dif_rel(v, alvo)
    return max(abs(x) for x in d.values()), d


def tarefa(arg):
    par, rot, alvo = arg
    l0 = par.pop("l0", 0.0)
    return rot, dif(par, l0, alvo)


if __name__ == "__main__":
    import multiprocessing as mp
    resA, _ = C.avaliar(C.A["q"], C.A["c1"], C.A["c2"], C.A["M"], 0.0, 0.0, freqs=(10.0,))
    alvo = C.fisicos(resA[0]["com"][0], C.A["iota"], C.A["M"], C.A["D"])
    pares = json.load(open(os.path.join(C.RES, "exp40_pares.json")))["pares"]
    tarefas = []
    for p in pares:
        if (p["e0"], p["qB"]) not in ((0.2, 2.0), (0.1, 1.2)):
            continue
        base = dict(p["depois"]["par"])
        tarefas.append((dict(base), "%s/%s ponto" % (p["e0"], p["qB"]), alvo))
        for eps in (1e-10, 1e-8, 1e-6):
            for k in ("M", "c1"):
                b = dict(base); b[k] = b[k] * (1 + eps)
                tarefas.append((b, "%s/%s %s*(1+%.0e)" % (p["e0"], p["qB"], k, eps), alvo))
        b = dict(base); b["l0"] = 1e-6
        tarefas.append((b, "%s/%s l0=1e-6" % (p["e0"], p["qB"]), alvo))
    with mp.get_context("spawn").Pool(2) as pool:
        out = pool.map(tarefa, tarefas)
    linhas = ["%-28s max|dif| %.2e  [%s]" % (rot, m, " ".join("%s %+.1e" % (k[:4], v) for k, v in d.items()))
              for rot, (m, d) in out]
    print("\n".join(linhas))
    open(os.path.join(C.RES, "ver_D8_pares_tremor.txt"), "w").write("\n".join(linhas) + "\n")
