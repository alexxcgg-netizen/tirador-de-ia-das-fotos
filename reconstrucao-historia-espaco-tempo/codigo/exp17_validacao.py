"""Experimento 17: validacao da infraestrutura do D1 (exp17_comum, exp17_fibra.Tabela).

(a) exp17_comum.memorias_varias (uma onda, muitas janelas, referencial 'ti') contra observaveis.memorias_observaveis
    (todos_m=True), maior diferenca relativa ao maior multipolo de cada tipo; q < 1 pela troca;
(b) termo de borda inicial dos m != 0 ('borda', relativo ao maior m = 0 do tipo) e convergencia da media sobre o inicio
    (n_orb = 2, 3, 5, 8 contra 3 com 256 pontos);
(c) erro do interpolante da tabela da fibra (diretorio em argv[1]) contra avaliacao direta em pontos aleatorios,
    no observador (iota = 50 graus, phi' = 0.7), T0 e T.
Saida: resultados/exp17_validacao.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402
import observaveis as O                                  # noqa: E402

SAIDA = os.path.join(AQUI, "..", "resultados", "exp17_validacao.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    log("(a) memorias_varias (referencial 'ti') contra observaveis.memorias_observaveis(todos_m=True)")
    for (q, c1, c2) in [(1.2, 0.3, -0.2), (3.0, 0.6, 0.0), (0.8, -0.2, 0.3)]:
        res = C.memorias_varias(q, c1, c2, [65.0, 80.0, 120.0])
        for r in res:
            M = r["aux"]["M"]
            if q < 1:
                mem, aux = O.memorias_observaveis(1 / q, c2, c1, M, 10.0, todos_m=True)
                mem = {tp: {k: v * (-1) ** k[1] for k, v in mem[tp].items()} for tp in mem}
            else:
                mem, aux = O.memorias_observaveis(q, c1, c2, M, 10.0, todos_m=True)
            dif = max(max(abs(v - r["mem_ti"][tp][k]) for k, v in mem[tp].items()) / max(abs(x) for x in mem[tp].values())
                      for tp in C.TIPOS)
            log("  (%.1f, %+.1f, %+.1f) M %.0f: dif max %.1e ; d M_f %.1e ; d t_i %.1e M ; borda inicial m != 0: %s"
                % (q, c1, c2, M, dif, r["aux"]["M_f"] - aux["M_f"], r["aux"]["t_i"] - aux["t_i"],
                   " ".join("%s %.1e" % (t[:4], v) for t, v in r["aux"]["borda"].items())))
    log("")
    log("(b) media sobre o inicio da janela (m != 0, referencial do pico): diferenca contra n_orb = 3, 256 pontos")
    ref = C.memorias_varias(1.2, 0.3, -0.2, [30.0, 65.0, 120.0], n_orb=3.0, n_media=256)
    for (no, nm) in [(2.0, 128), (3.0, 128), (5.0, 192), (8.0, 384)]:
        rr = C.memorias_varias(1.2, 0.3, -0.2, [30.0, 65.0, 120.0], n_orb=no, n_media=nm)
        out = []
        for r, r0 in zip(rr, ref):
            d = max(max(abs(r["mem_pico"][t][k] - r0["mem_pico"][t][k]) for k in r0["mem_pico"][t] if k[1] != 0)
                    / max(abs(v) for k, v in r0["mem_pico"][t].items() if k[1] == 0) for t in C.TIPOS)
            out.append("M %.0f: %.1e" % (r["aux"]["M"], d))
        log("  n_orb %.0f, %d pontos: %s" % (no, nm, " ; ".join(out)))
    if len(sys.argv) > 1:
        import exp17_fibra as F
        pasta = sys.argv[1]
        z = np.load(os.path.join(pasta, "chaves.npz"))
        K = {t: [tuple(int(a) for a in x) for x in z[t]] for t in C.TIPOS}
        rng = np.random.default_rng(7)
        log("")
        log("(c) erro relativo do interpolante da tabela no observador (iota 50, phi' 0.7): max sobre as quatro memorias")
        errs0, errsT = [], []
        for (qB, c2B) in [(1.0, -0.0), (1.5, 0.2), (2.0, 0.4), (2.75, -0.2), (3.5, 0.6), (4.0, 0.8)]:
            tab = F.Tabela(pasta, qB, c2B, K)
            for _ in range(3):
                c1 = rng.uniform(-0.8, 0.8)
                M = np.exp(rng.uniform(np.log(46), np.log(128)))
                Xi = tab.interp([c1], [M])[0, 0]
                r = C.memorias_varias(qB, c1, c2B, [M])[0]
                Xe = np.concatenate([np.array([r["mem_pico"][t][k] for k in K[t]]) for t in C.TIPOS])
                Y0 = tab.Y([np.radians(50.0)], 0.7, True)
                YT = tab.Y([np.radians(50.0)], 0.7, False)
                e0 = np.max(np.abs(F.projetar(Xi, Y0)[0] / F.projetar(Xe, Y0)[0] - 1))
                eT = np.max(np.abs(F.projetar(Xi, YT)[0] / F.projetar(Xe, YT)[0] - 1))
                errs0.append(e0)
                errsT.append(eT)
                log("  q_B %.2f chi2_B %+.1f chi1 %+.3f M %.1f: T0 %.1e ; T %.1e" % (qB, c2B, c1, M, e0, eT))
        log("  mediana / maximo: T0 %.1e / %.1e ; T %.1e / %.1e" % (np.median(errs0), max(errs0), np.median(errsT), max(errsT)))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(linhas) + "\n")
