"""Revisao R1: quanto pesam no observador os multipolos m != 0 das memorias (secao 1.2 do 07).

O 07 descarta os multipolos m != 0 como "termo de borda da janela". O termo de borda do fim da janela,
porem, e fixado pela fusao e nao some: depois do ringdown o integrando oscilante ja decaiu e o valor
acumulado fica constante (dependente da fase orbital na fusao). Aqui:
  - memorias de todos os (l, m) do sistema A (nivel A, NRHybSur3dq8_CCE, janela desde 10 Hz);
  - valor no observador (iota = 50 graus) em funcao do azimute phi, com e sem os m != 0;
  - o mesmo com o inicio da janela suavizado (rampa de 3000 M), para separar a borda inicial
    (artefato da janela) da borda final (fisica);
  - mesma conta para o par B (q = 2, chi2 = 0) do exp07: os pares do 07 continuam iguais com m != 0?
Saida: resultados/revisao/rev_R1_m_nao_nulo.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
import deteccao as Dt                                    # noqa: E402
from harmonicos import sYlm, Dfrak, ethb2_de_escalar      # noqa: E402
from memorias import gram                                 # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1_m_nao_nulo.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def memorias_todas(q, c1, c2, M, rampa_s=0.0, dt=0.25):
    """Memorias nulas de todos os (l, m) (nivel A) + ordinaria de CM; deslocamento so da janela."""
    t, h = B.gerar(q, c1, c2, f0=M * Dt.MSUN_S * 10.0, dt=dt)
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    del h
    if rampa_s > 0:
        n = int(rampa_s / (M * Dt.MSUN_S) / dt)
        H[:n] *= (0.5 * (1 - np.cos(np.pi * np.arange(n) / n)))[:, None]
    Hd = B.derivada4(H, dt)
    calc = B.calculadoras()[0]
    m = calc.memorias_gram(*gram(H, Hd, dt))
    del H, Hd
    eta = q / (1 + q) ** 2
    x0 = (np.pi * M * Dt.MSUN_S * 10.0) ** (2 / 3)
    Mf = 1 - (m["energia_total"] + 0.5 * eta * x0 * (1 + x0 * (-0.75 - eta / 12)))     # como em binarias.memorias
    pre = {(2, 0): B.favata_h20(x0, eta), (4, 0): B.lrr_h40(x0, eta)}
    out = {k: {} for k in B.TIPOS}
    for (l, mm), v in m["deslocamento"].items():
        if l <= 8:
            out["deslocamento"][(l, mm)] = v + pre.get((l, mm), 0.0)
    for (l, mm), v in m["spin"].items():
        if l <= 8:
            out["spin"][(l, mm)] = v
    for (l, mm), v in m["giroscopica"].items():
        if l <= 8:
            out["giroscopica"][(l, mm)] = v
    for (l, mm), v in m["cm"].items():
        if l <= 8:
            dJ = out["deslocamento"][(l, mm)]
            out["cm"][(l, mm)] = v + 0.5 * ethb2_de_escalar(l) * (-1.5 * Mf * (2 * dJ / ethb2_de_escalar(l)) / Dfrak(l))
    return out


def observador(mem, iota, phi, so_m0):
    vals = {}
    for tipo in B.TIPOS:
        s = 0 if tipo == "giroscopica" else -2
        z = sum(c * sYlm(s, l, m, iota, phi) for (l, m), c in mem[tipo].items() if (m == 0 or not so_m0))
        vals[tipo] = float(-np.imag(z)) if tipo == "spin" else float(np.real(z))
    return vals


with open(os.path.join(AQUI, "..", "..", "resultados", "exp07_pares.json")) as fh:
    J = json.load(fh)
A = J["A"]
phis = np.linspace(0, 2 * np.pi, 13)[:-1]
for nome_r, rampa in (("janela abrupta (como no 07)", 0.0), ("inicio suavizado em 1 s", 1.0)):
    memA = memorias_todas(A["q"], A["c1"], A["c2"], A["M"], rampa)
    log("Sistema A, %s, iota = 50 graus:" % nome_r)
    base = observador(memA, A["iota"], 0.0, True)
    for tipo in B.TIPOS:
        rel = [observador(memA, A["iota"], ph, False)[tipo] / base[tipo] - 1 for ph in phis]
        log("  %-13s (todos os m)/(so m = 0) - 1 ao longo de phi: min %+.2e max %+.2e" % (tipo, min(rel), max(rel)))
    for tipo in B.TIPOS:
        maior = max(((k, abs(v)) for k, v in memA[tipo].items() if k[1] != 0), key=lambda kv: kv[1])
        m0 = max(abs(v) for k, v in memA[tipo].items() if k[1] == 0)
        log("    %-13s maior multipolo m != 0: %s com |.| = %.2e ; maior m = 0: %.2e" % (tipo, maior[0], maior[1], m0))

# par B (q = 2, chi2 = 0): diferenca das quatro memorias com e sem m != 0
p = [pp for pp in J["pares"] if pp["qB"] == 2.0 and pp["c2B"] == 0.0][0]
memA = memorias_todas(A["q"], A["c1"], A["c2"], A["M"], 0.0)
memB = memorias_todas(p["qB"], p["c1"], p["c2B"], p["M"], 0.0)
log("")
log("Par (q_B = 2, chi2 = 0), janela abrupta como no 07: (B - A)/|A| no observador (unidades fisicas)")
for ph in (0.0, np.pi / 2, np.pi, 3 * np.pi / 2):
    for so_m0 in (True, False):
        vA = observador(memA, A["iota"], ph, so_m0)
        vB = observador(memB, p["iota"], ph, so_m0)
        fA = {"deslocamento": A["M"] / A["D"], "spin": A["M"] ** 2 / A["D"], "cm": A["M"] ** 2 / A["D"],
              "giroscopica": (A["M"] / A["D"]) ** 2}
        fB = {"deslocamento": p["M"] / p["D"], "spin": p["M"] ** 2 / p["D"], "cm": p["M"] ** 2 / p["D"],
              "giroscopica": (p["M"] / p["D"]) ** 2}
        d = {k: (vB[k] * fB[k] - vA[k] * fA[k]) / abs(vA[k] * fA[k]) for k in B.TIPOS}
        log("  phi = %5.1f graus, %-10s: %s" % (np.degrees(ph), "so m = 0" if so_m0 else "todos os m",
                                                ", ".join("%s %+.1e" % (k, v) for k, v in d.items())))
log("(o par foi construido no 07 com o deslocamento total e a fase orbital do substituto; phi e o azimute do observador"
    " em relacao a essa fase, desconhecido e igual para A e B so por convencao)")
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(linhas) + "\n")
