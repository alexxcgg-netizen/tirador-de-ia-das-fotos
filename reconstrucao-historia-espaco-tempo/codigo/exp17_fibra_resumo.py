"""Experimento 17 (L02): junta as partes da busca da fibra, completa o polimento e resume.

1. junta resultados/exp17_fibra_0_60.json e _60_117.json em resultados/exp17_fibra.json;
2. polimento exato (exp17_resolver) dos minimos T0 INTERIORES ainda nao polidos com residuo do interpolante < 1e-2
   (o erro do interpolante chega a ~4e-4, entao um minimo de 1e-3 pode esconder uma solucao exata);
3. classifica cada ponto (q_B, chi2_B): solucoes exatas (residuo < 1e-8, dentro do dominio), minimos na borda
   |chi1| = 0.8 (a folha sai do dominio), minimos interiores nao nulos (dobra: o par de solucoes desapareceu);
4. T: para cada phi'_B, solucoes do interpolante com residuo < 1e-6 fora da borda.
5. conexidade: componentes conexas (vizinhanca de 4 na grade) dos pontos com solucao exata na folha principal;
   continuidade das solucoes entre vizinhos (saltos de chi1, M, iota).
Saidas: resultados/exp17_fibra.json (com o polimento extra), resultados/exp17_fibra_resumo.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_resolver as R                               # noqa: E402

RES = os.path.join(AQUI, "..", "resultados")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def interior(s):
    return abs(abs(s["chi1"]) - 0.8) > 1e-6 and 45.5 < s["M"] < 129.5


if __name__ == "__main__":
    partes = [json.load(open(os.path.join(RES, n))) for n in ("exp17_fibra_0_60.json", "exp17_fibra_60_117.json")]
    d = dict(alvo_T0=partes[0]["alvo_T0"], alvo_T=partes[0]["alvo_T"], pontos={})
    for p in partes:
        d["pontos"].update(p["pontos"])
    a0 = np.array(d["alvo_T0"])
    alvo0 = dict(zip(R.TIPOS, a0))
    extra = 0
    for k, reg in d["pontos"].items():
        for s in reg["T0"]:
            if "exato" not in s and interior(s) and s["res_interp"] < 1e-2:
                rs = R.Resolvedor(alvo0, reg["qB"], reg["c2B"], "T0")
                p = rs.resolver((s["iota"], s["chi1"], s["M"]), max_nfev=15)
                s["exato"] = dict(iota=p["iota"], chi1=p["chi1"], M=p["M"], D=p["D"], res=p["res"], M_f=p["M_f"],
                                  E_janela=p["E_janela"], E_lig=p["E_lig"], no_limite=p["no_limite"], ondas=p["ondas"])
                s.pop("borda", None)
                extra += 1
    log("Polimento extra de %d minimos interiores (residuo do interpolante entre 1e-3 e 1e-2)" % extra)
    with open(os.path.join(RES, "exp17_fibra.json"), "w") as fh:
        json.dump(d, fh, indent=0)
    qs = sorted(set(v["qB"] for v in d["pontos"].values()))
    cs = sorted(set(v["c2B"] for v in d["pontos"].values()))
    tab = {}
    log("")
    log("Por ponto: E = solucoes exatas T0 (residuo < 1e-8, dentro do dominio); b = minimos na borda |chi1| = 0.8 (residuo);")
    log("i = minimos interiores sem solucao (residuo exato); T = numero de phi'_B (de 8) com solucao T (residuo do interpolante < 1e-6)")
    for c in cs[::-1]:
        lin = []
        for q in qs:
            reg = d["pontos"]["%.2f|%+.2f" % (q, c)]
            ex = [s["exato"] for s in reg["T0"] if "exato" in s and s["exato"]["res"] < 1e-8 and not s["exato"]["no_limite"]]
            bo = [s["res_interp"] for s in reg["T0"] if not interior(s)]
            it = [s["exato"]["res"] for s in reg["T0"] if "exato" in s and (s["exato"]["res"] >= 1e-8 or s["exato"]["no_limite"])]
            nT = sum(any(x["res_interp"] < 1e-6 and interior(x) for x in v) for v in reg["T"].values())
            nT2 = max(sum(1 for x in v if x["res_interp"] < 1e-6 and interior(x)) for v in reg["T"].values())
            tab[(q, c)] = dict(ex=ex, bo=bo, it=it, nT=nT, nT2=nT2)
            lin.append("%dE%s%s T%d%s" % (len(ex), (" b%.0e" % min(bo)) if bo else "", (" i%.0e" % min(it)) if it else "", nT,
                                          ("(2)" if nT2 > 1 else "")))
        log("chi2_B %+.1f | " % c + " | ".join("%-22s" % x for x in lin))
    log("q_B:          " + " | ".join("%-22.2f" % q for q in qs))
    # conexidade da folha principal (uma solucao exata por ponto na folha que contem A: a de menor |chi1 - continuidade|)
    pts = {k: v["ex"] for k, v in tab.items() if v["ex"]}
    nex = sum(len(v) for v in pts.values())
    multi = [k for k, v in pts.items() if len(v) > 1]
    log("")
    log("Pontos com solucao exata: %d de %d ; solucoes exatas: %d ; pontos com mais de uma: %d %s"
        % (len(pts), len(tab), nex, len(multi), multi))
    viz = {}
    for (q, c) in pts:
        i, j = qs.index(q), cs.index(c)
        viz[(q, c)] = [(qs[a], cs[b]) for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))
                       if 0 <= a < len(qs) and 0 <= b < len(cs) and (qs[a], cs[b]) in pts]
    vistos, comps = set(), []
    for k in pts:
        if k in vistos:
            continue
        pilha, comp = [k], []
        while pilha:
            u = pilha.pop()
            if u in vistos:
                continue
            vistos.add(u)
            comp.append(u)
            pilha += viz[u]
        comps.append(comp)
    log("Componentes conexas (vizinhanca 4) dos pontos com solucao: %d, tamanhos %s" % (len(comps), [len(c) for c in comps]))
    saltos = []
    for k, vs in viz.items():
        for u in vs:
            a, b = pts[k][0], pts[u][0]
            saltos.append((abs(a["chi1"] - b["chi1"]), abs(a["M"] - b["M"]), abs(np.degrees(a["iota"] - b["iota"])), k, u))
    s = np.array([x[:3] for x in saltos])
    log("Saltos entre vizinhos (primeira solucao): max |d chi1| %.3f, max |d M| %.2f, max |d iota| %.2f graus" % tuple(s.max(axis=0)))
    allv = [x for v in pts.values() for x in v]
    for nm in ("chi1", "M", "D", "iota"):
        v = np.array([x[nm] for x in allv])
        if nm == "iota":
            v = np.degrees(v)
        log("  faixa de %-5s nas solucoes exatas: %.4f a %.4f" % (nm, v.min(), v.max()))
    Mf = np.array([x["M_f"] * x["M"] for x in allv])
    log("  M_f fisico (M_sol): %.3f a %.3f (A: %.3f)" % (Mf.min(), Mf.max(), 0.949766 * 65))
    with open(os.path.join(RES, "exp17_fibra_resumo.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
