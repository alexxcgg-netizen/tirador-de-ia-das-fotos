"""Verificacao adversarial D1: solucoes relatadas (pares, dobra, curva T com iota e D conhecidos, polo, reflexao).

(1) T0 (so m = 0) por caminho independente (observaveis.memorias_observaveis, uma onda por avaliacao), dt = 0.25 e
    0.125: A, pares (2,0) e (2,+0.5) resolvidos (exp17_pares.json), as duas solucoes da dobra em (q_B, chi2_B) =
    (3, -0.2) e o ponto extremo (3, +0.8) (exp17_fibra.json). Diferenca relativa por observavel em relacao a A.
(2) T (todos os m) na curva com iota e D conhecidos (exp17_fibra_iD.json, pontas phi' = -0.982 e +0.589) com
    exp17_comum.memorias_varias em quatro definicoes dos m != 0: (dt 0.25, media de Hann 3 orbitas) = a do relatorio,
    (dt 0.125, 3 orbitas), (dt 0.25, 6 orbitas), (janela abrupta, sem media). Se a curva e propriedade robusta, o
    residuo deve ficar pequeno em todas.
(3) Polo (iota = 0): valores de T relativos aos de iota = 50 graus nas mesmas quatro definicoes.
(4) Reflexao: F(pi - iota)/F(iota) com todos os m (observaveis, referencial 'ti').
Saida: resultados/ver_D1_pontos.txt
"""
import json
import os
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
RES = os.path.join(AQUI, "..", "..", "resultados")
SAIDA = os.path.join(RES, "ver_D1_pontos.txt")
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")


def t0(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    import observaveis as O
    nome, q, c1, c2, M, D, iota, dt = arg
    m, a = O.memorias_observaveis(q, c1, c2, M, 10.0, dt=dt)
    v = O.valores_fisicos_completo(m, iota, 0.0, M, D)
    return nome, dt, np.array([v[k] for k in TIPOS]), a["M_f"] * M


def tT(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    import exp17_comum as C
    nome, q, c1, c2, M, D, iota, phi, defin = arg
    dt, media, n_orb = defin
    r = C.memorias_varias(q, c1, c2, [M], dt=dt, media=media, n_orb=n_orb)[0]
    mem = r["mem_pico"]
    out = {"v": C.vetor_fisico(mem, iota, phi, M, D)}
    if nome == "A":
        out["polo"] = C.vetor_fisico(mem, 0.0, phi, M, D)
        out["polo_phi1"] = C.vetor_fisico(mem, 0.0, phi + 1.0, M, D)
        out["v50_m0"] = C.vetor_fisico(C.so_m0(mem), iota, phi, M, D)
    return nome, defin, out


def refl(_):
    os.environ["OMP_NUM_THREADS"] = "1"
    import observaveis as O
    m, a = O.memorias_observaveis(1.2, 0.3, -0.2, 65.0, 10.0, todos_m=True)
    out = []
    for io in (0.3, 0.8726646259971648, 1.3):
        for phi in (0.0, 1.1, 2.5):
            v1 = O.no_observador_completo(m, io, phi)
            v2 = O.no_observador_completo(m, np.pi - io, phi)
            out.append((io, phi, np.array([v2[k] / v1[k] for k in TIPOS])))
    return out


if __name__ == "__main__":
    import multiprocessing as mp
    pares = json.load(open(os.path.join(RES, "exp17_pares.json")))
    fib = json.load(open(os.path.join(RES, "exp17_fibra.json")))["pontos"]
    iD = json.load(open(os.path.join(RES, "exp17_fibra_iD.json")))["curva"]
    io50 = np.radians(50.0)
    lst = [("A", 1.2, 0.3, -0.2, 65.0, 400.0, io50)]
    for p in pares["pares"]:
        if (p["qB"], p["c2B"]) in ((2.0, 0.0), (2.0, 0.5)):
            s = p["T0"]
            lst.append(("par (%.0f, %+.1f)" % (p["qB"], p["c2B"]), p["qB"], s["chi1"], p["c2B"], s["M"], s["D"], s["iota"]))
    for k, nm in (("3.00|-0.20", "dobra (3,-0.2)"), ("3.00|+0.80", "extremo (3,+0.8)")):
        for j, s in enumerate(fib[k]["T0"]):
            if "exato" in s:
                e = s["exato"]
                lst.append(("%s sol%d" % (nm, j), fib[k]["qB"], e["chi1"], fib[k]["c2B"], e["M"], e["D"], e["iota"]))
    args0 = [x + (dt,) for x in lst for dt in (0.25, 0.125)]
    DEFS = [(0.25, True, 3.0), (0.125, True, 3.0), (0.25, True, 6.0), (0.25, False, 3.0)]
    pts = [("A", 1.2, 0.3, -0.2, 65.0, 400.0, io50, 0.0)]
    for c in iD:
        if abs(c["phi"] + 0.9817) < 1e-3 or abs(c["phi"] - 0.5890) < 1e-3:
            pts.append(("curva phi'=%+.3f" % c["phi"], c["q"], c["c1"], c["c2"], c["M"], 400.0, io50, c["phi"]))
    argsT = [x + (d,) for x in pts for d in DEFS]
    with mp.get_context("spawn").Pool(2) as pool:
        r0 = pool.map(t0, args0, chunksize=1)
        rT = pool.map(tT, argsT, chunksize=1)
        rr = pool.map(refl, [0])[0]
    L = []

    def log(s=""):
        print(s, flush=True)
        L.append(s)

    log("(1) T0 por observaveis (caminho independente); B/A - 1 por (desl, spin, CM, giro); M_f fisico (M_sol)")
    ref = {dt: v for (n, dt, v, mf) in r0 if n == "A"}
    for (n, dt, v, mf) in r0:
        log("  %-26s dt %.3f  F = %s  F/F_A - 1 = %s  M_f M = %.3f" % (n, dt, np.array2string(v, precision=6),
                                                                       np.array2string(v / ref[dt] - 1, precision=2), mf))
    log("")
    log("(2) T na curva (iota, D conhecidos); definicoes (dt, media, n_orb); B/A - 1 com A na mesma definicao")
    refT = {d: o["v"] for (n, d, o) in rT if n == "A"}
    for (n, d, o) in rT:
        if n != "A":
            log("  %-18s %-20s B/A - 1 = %s" % (n, str(d), np.array2string(o["v"] / refT[d] - 1, precision=2)))
    log("  A em cada definicao relativo a (0.25, True, 3):")
    for (n, d, o) in rT:
        if n == "A":
            log("    %-20s %s ; T/T0 - 1 = %s" % (str(d), np.array2string(o["v"] / refT[DEFS[0]] - 1, precision=2),
                                               np.array2string(o["v"] / o["v50_m0"] - 1, precision=3)))
    log("")
    log("(3) Polo iota = 0, A: T(0)/T0(50 graus) por definicao (giro = m = 0 puro), e com phi' + 1 rad")
    for (n, d, o) in rT:
        if n == "A":
            log("    %-20s %s | phi'+1: %s" % (str(d), np.array2string(o["polo"] / o["v50_m0"], precision=3),
                                              np.array2string(o["polo_phi1"] / o["v50_m0"], precision=3)))
    log("")
    log("(4) Reflexao, todos os m: F(pi - iota)/F(iota) (esperado 1, -1, 1, -1)")
    for io, phi, x in rr:
        log("    iota %.3f phi %.1f: %s ; max desvio %.1e" % (io, phi, np.array2string(x, precision=10),
                                                         np.max(np.abs(np.abs(x) - 1))))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(L) + "\n")
