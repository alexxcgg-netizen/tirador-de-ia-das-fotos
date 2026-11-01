"""Experimento 40, parte 5 (linha L16, tarefa 3): jacobiano das duas janelas em A com as direcoes excentricas.

Perto de e0 = 0 a dependencia em (e0, l0) e, em primeira ordem, linear em e0 com um harmonico em l0
(exp40_anomalia): F(e0, l0) - F(0) ~ e0 (a cos l0 + b sin l0) + O(e0^2). Nas variaveis X = e0 cos l0,
Y = e0 sin l0 o mapa e suave em A. Mede:
  a) o jacobiano 7 x 7 dos residuos (D eliminado pelo deslocamento da 1a janela) em A, com colunas
     (iota, chi1, M, q, chi2) por diferencas centrais de passo grande e colunas (X, Y) pelo 1o harmonico em l0
     com e0 = 0,03 e 0,06 (4 valores de l0); valores singulares com e sem (X, Y);
  b) o termo de 2a ordem (media em l0) e a linearidade em e0;
  c) quatro buscas locais a partir dos pontos da familia circular de duas janelas achados no exp40_duas_janelas
     (controles), com e0 = 0,03 e l0 = 0 ou pi, para ver se a excentricidade abaixa o piso da familia.
Saida: resultados/exp40_jacobiano.txt e .json
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp40_comum as C                                 # noqa: E402
import exp40_duas_janelas as DJ                         # noqa: E402

ESC = np.array([0.01, 0.1, 1.0, 0.1, 0.1, 0.1, 0.1])    # escala das colunas (iota rad, chi1, M_sol, q, chi2, X, Y)
NOMES_P = ("iota", "chi1", "M", "q", "chi2", "X", "Y")


def r_circ(p, alvo):
    return DJ.residuos(p, alvo, e0_fixo=0.0)[0]


def r_exc(p5, e0, l0, alvo):
    return DJ.residuos(list(p5) + [e0, l0], alvo)[0]


def coluna(arg):
    tipo, k, h, alvo, p0 = arg
    if tipo == "c":
        pp, pm = list(p0), list(p0)
        pp[k] += h
        pm[k] -= h
        return (tipo, k, h), (r_circ(pp, alvo) - r_circ(pm, alvo)) / (2 * h)
    e0, l0 = k, h
    return (tipo, e0, l0), r_exc(p0, e0, l0, alvo)


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    resA, _ = C.avaliar(C.A["q"], C.A["c1"], C.A["c2"], C.A["M"], 0.0, 0.0)
    alvo = [C.fisicos(r["com"][0], C.A["iota"], C.A["M"], C.A["D"]) for r in resA]
    p0 = [C.A["iota"], C.A["c1"], C.A["M"], C.A["q"], C.A["c2"]]
    passos = [0.01, 0.01, 0.065, 0.01, 0.01]
    tarefas = [("c", k, passos[k], alvo, p0) for k in range(5)]
    tarefas += [("c", k, passos[k] / 2, alvo, p0) for k in range(5)]
    for e0 in (0.03, 0.06):
        for l0 in (0.0, np.pi / 2, np.pi, 3 * np.pi / 2):
            tarefas.append(("e", e0, l0, alvo, p0))
    with mp.get_context("spawn").Pool(2) as pool:
        out = dict(pool.map(coluna, tarefas))
        # buscas locais a partir dos controles circulares do exp40_duas_janelas
        sols = json.load(open(os.path.join(C.RES, "exp40_duas_janelas.json")))["solucoes"]
        ctrl = [s["x"] for s in sols if s["e0_fixo"] is not None]
        buscas = []
        for xc in ctrl:
            for l0 in (0.0, np.pi):
                buscas.append((alvo, list(xc) + [0.03, l0], None, "controle q=%.3f + e0=0.03, l0=%.2f" % (xc[3], l0)))
        res_b = pool.map(DJ.resolver, buscas)
    r0 = r_circ(p0, alvo)
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)
    log("exp40_jacobiano: duas janelas (10 e 20 Hz), 7 residuos (D eliminado), em A (SEOBNRv5EHM com as correcoes)")
    log("residuo em A (deve ser o tremor): " + " ".join("%+.1e" % x for x in r0))
    Jc = np.stack([out[("c", k, passos[k])] for k in range(5)], axis=1)
    Jc2 = np.stack([out[("c", k, passos[k] / 2)] for k in range(5)], axis=1)
    log("colunas circulares, erro relativo passo h x h/2: " + " ".join(
        "%s %.1e" % (NOMES_P[k], np.linalg.norm(Jc[:, k] - Jc2[:, k]) / np.linalg.norm(Jc[:, k])) for k in range(5)))
    cols = {}
    for e0 in (0.03, 0.06):
        rr = {l0: out[("e", e0, l0)] for l0 in (0.0, np.pi / 2, np.pi, 3 * np.pi / 2)}
        a = (rr[0.0] - rr[np.pi]) / (2 * e0)
        b = (rr[np.pi / 2] - rr[3 * np.pi / 2]) / (2 * e0)
        c = (rr[0.0] + rr[np.pi] + rr[np.pi / 2] + rr[3 * np.pi / 2]) / 4 - r0
        cols[e0] = (a, b, c)
        log("e0 = %.2f: dF/dX = %s" % (e0, " ".join("%+.2e" % x for x in a)))
        log("          dF/dY = %s" % " ".join("%+.2e" % x for x in b))
        log("          media em l0 - F(A) = %s (termo ~ e0^2)" % " ".join("%+.1e" % x for x in c))
    a3, b3, c3 = cols[0.03]
    a6, b6, c6 = cols[0.06]
    log("linearidade: |dF/dX(0.06) - dF/dX(0.03)|/|dF/dX| = %.2f ; idem Y %.2f ; razao das medias (0.06/0.03) = %.2f (e0^2 -> 4)"
        % (np.linalg.norm(a6 - a3) / np.linalg.norm(a3), np.linalg.norm(b6 - b3) / np.linalg.norm(b3),
           np.linalg.norm(c6) / max(np.linalg.norm(c3), 1e-30)))
    J7 = np.concatenate([Jc, a3[:, None], b3[:, None]], axis=1) * ESC[None, :]
    J5 = Jc * ESC[None, :5]
    s5 = np.linalg.svd(J5, compute_uv=False)
    U, s7, Vt = np.linalg.svd(J7)
    log("valores singulares (colunas escaladas por %s):" % ESC)
    log("  circular (7 x 5): " + " ".join("%.2e" % x for x in s5))
    log("  com X, Y (7 x 7): " + " ".join("%.2e" % x for x in s7))
    log("  direcao mais fraca (7 x 7), em unidades da escala: " + " ".join("%s %+.3f" % (n, v) for n, v in zip(NOMES_P, Vt[-1])))
    J7b = np.concatenate([Jc, a6[:, None], b6[:, None]], axis=1) * ESC[None, :]
    log("  com X, Y de e0 = 0,06: " + " ".join("%.2e" % x for x in np.linalg.svd(J7b, compute_uv=False)))
    # passo linear minimo para um residuo de tremor (1e-5): |dx| ~ 1e-5 / s_min em unidades de escala
    log("  deslocamento (em unidades de escala) que muda os residuos so 1e-5 na direcao mais fraca: %.1e" % (1e-5 / s7[-1]))
    log()
    log("buscas locais a partir da familia circular de duas janelas, com e0 e l0 livres:")
    for s in res_b:
        x = s["x"]
        log("  %s: max|res| %.2e -> iota %.2f graus chi1 %+.4f M %.3f q %.3f chi2 %+.4f e0 %.4f l0 %.3f (%.0f s)"
            % (s["rotulo"], s["max_res"], np.degrees(x[0]), x[1], x[2], x[3], x[4], x[5], x[6] % (2 * np.pi), s["tempo_s"]))
        log("      residuos: " + " ".join("%+.1e" % r for r in s["res"]))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(C.RES, "exp40_jacobiano.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(C.RES, "exp40_jacobiano.json"), "w") as f:
        json.dump(dict(J7=J7.tolist(), s5=s5.tolist(), s7=s7.tolist(), buscas=res_b), f, indent=1, default=float)
