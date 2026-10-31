"""Revisao R2, item 5: expoentes do exp13 (massas iguais, direcao chi_a) com mais valores de d.

O 07 (§3.1, §3.2) afirma: memorias globais ~ d^2.0 no nivel A e ~ d^1.0 no nivel C (violacao da simetria
de troca pelo substituto); 1 - match ~ d^2.0. O exp13 so imprime o expoente do nivel C, com 4 valores de d.
Aqui:
  - mais valores de d (0.0125 ate 0.3 para chi_s = -0.5, limite |chi| <= 0.8; ate 0.5 para chi_s = +0.3);
  - expoentes nos niveis A e C, por ajuste global e por inclinacao local;
  - decomposicao exata em parte par e impar em chi_a, calculando tambem o sistema trocado (chi_s - d, chi_s + d):
      par(d)   = [v(+d) + v(-d)]/2 - v(0)     (a simetria preve ~ d^2)
      impar(d) = [v(+d) - v(-d)]/2            (a simetria preve 0; mede a violacao)
  - 1 - match com a busca no tempo do exp07 e com busca 16 vezes mais fina (rev_R2_comum).
Saida: resultados/revisao/rev_R2_exp13_expoentes.txt e .json
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import rev_R2_comum as C                                # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
M, D, IOTA, F = 65.0, 400.0, np.radians(50.0), 10.0
LISTA = B.lista_osc() + B.MODOS_M0
linhas = []
NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def vet(c1, c2):
    """Vetor global (7 multipolos) nos niveis A e C, com uma unica geracao da onda (janela M f0 = 0.004)."""
    t, h = B.gerar(1.0, c1, c2)
    return {n: B.vetor(B.memorias(1.0, c1, c2, nivel=n, t=t, h=h)[0])[0] for n in ("A", "C")}


def strain(c1, c2):
    t, h = B.gerar(1.0, c1, c2, f0=M * Dt.MSUN_S * F)
    return Dt.strain_observador(t, h, LISTA, M, D, IOTA)


def expo(ds, ys):
    ds, ys = np.asarray(ds), np.asarray(ys)
    ok = ys > 0
    return np.polyfit(np.log(ds[ok]), np.log(ys[ok]), 1)[0] if ok.sum() >= 2 else np.nan


def locais(ds, ys):
    return [np.log(ys[i + 1] / ys[i]) / np.log(ds[i + 1] / ds[i]) for i in range(len(ds) - 1)]


saida = {}
for chi_s, deltas in ((-0.5, [0.0125, 0.025, 0.05, 0.1, 0.2, 0.3]),
                      (0.3, [0.0125, 0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5])):
    log("chi_s = %+.1f (q = 1): B = (chi_s + d, chi_s - d), B' = (chi_s - d, chi_s + d), A = (chi_s, chi_s)" % chi_s)
    v0 = vet(chi_s, chi_s)
    tsA, sA = strain(chi_s, chi_s)
    reg = dict(d=deltas, rel={"A": [], "C": []}, par={"A": [], "C": []}, impar={"A": [], "C": []},
               arg={"A": [], "C": []}, mism=[], mism16=[], snrA=None)
    for d in deltas:
        vp = vet(chi_s + d, chi_s - d)
        vm = vet(chi_s - d, chi_s + d)
        partes = {}
        for n in ("A", "C"):
            rel = np.abs((vp[n] - v0[n]) / v0[n])
            par = np.abs(((vp[n] + vm[n]) / 2 - v0[n]) / v0[n])
            imp = np.abs(((vp[n] - vm[n]) / 2) / v0[n])
            reg["rel"][n].append(float(rel.max()))
            reg["par"][n].append(float(par.max()))
            reg["impar"][n].append(float(imp.max()))
            reg["arg"][n].append(NOMES[int(np.argmax(rel))])
            partes[n] = (rel.max(), NOMES[int(np.argmax(rel))], par.max(), imp.max())
        tsB, sB = strain(chi_s + d, chi_s - d)
        c1 = C.comparar(tsA, sA, tsB, sB, "aLIGO", F)
        c16 = C.comparar(tsA, sA, tsB, sB, "aLIGO", F, up=16)
        reg["mism"].append(1 - c1["match"])
        reg["mism16"].append(1 - c16["match"])
        reg["snrA"] = c1["snr_A"]
        del tsB, sB
        log("  d = %.4f: nivel A max %.3e (%s; par %.3e, impar %.3e) | nivel C max %.3e (%s; par %.3e, impar %.3e) | "
            "1-match %.3e (busca x16: %.3e)"
            % (d, partes["A"][0], partes["A"][1], partes["A"][2], partes["A"][3],
               partes["C"][0], partes["C"][1], partes["C"][2], partes["C"][3], 1 - c1["match"], 1 - c16["match"]))
    ds = np.array(deltas)
    orig = [i for i, d in enumerate(deltas) if d in (0.025, 0.05, 0.1, 0.2)]
    for chave, nome in (("rel", "max dif."), ("par", "parte par"), ("impar", "parte impar")):
        for n in ("A", "C"):
            y = np.array(reg[chave][n])
            log("  expoente %-11s nivel %s: todos os d %.2f ; d do exp13 (0.025-0.2) %.2f ; locais %s"
                % (nome, n, expo(ds, y), expo(ds[orig], y[orig]),
                   " ".join("%.2f" % s for s in locais(ds, y))))
    for chave, nome in (("mism", "1-match (base)"), ("mism16", "1-match (x16)")):
        y = np.array(reg[chave])
        log("  expoente %-15s: todos os d %.2f ; d do exp13 %.2f ; locais %s"
            % (nome, expo(ds, y), expo(ds[orig], y[orig]), " ".join("%.2f" % s for s in locais(ds, y))))
    log("")
    saida[str(chi_s)] = reg
with open(os.path.join(RES, "revisao", "rev_R2_exp13_expoentes.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(RES, "revisao", "rev_R2_exp13_expoentes.json"), "w") as f:
    json.dump(saida, f, indent=1, default=float)
