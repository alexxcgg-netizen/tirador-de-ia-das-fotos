"""Verificador R4v, itens 4 e 5: dependencia das memorias em l0 (anomalia relativistica inicial, SEOBNRv5EHM).

 a) item 4: sistema da parte 2 do exp12 (M = 65, q = 1.2, chi = (0.3, -0.2)), e0 = 0.1 e 0.2, l0 = 0, pi/2, pi,
    3 pi/2: desl20, spin30, giro10 relativos ao circular (l0 = 0 deve reproduzir o exp12);
 b) item 5: B (e0 = 0.2, q_B = 2) do exp12, l0 = 0 x pi. Memorias acumuladas em subjanelas [t_pico - T, fim]
    e na primeira parte da janela [t0, t0 + 2 periodos orbitais]: a diferenca l0 = pi x 0 vem do inicio
    da janela (borda) ou do fim da inspiral e da fusao?
Saida: resultados/revisao/rev_R4v_anomalia.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
COD = os.path.dirname(AQUI)
RAIZ = os.path.dirname(COD)
sys.path.insert(0, COD)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import exp12_excentricas_imr as E                       # noqa: E402

RES = os.path.join(RAIZ, "resultados", "revisao")
linhas = []
NOMES = E.NOMES
IDX = [0, 2, 5]                                         # desl20, spin30, giro10


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def gerar_l0(q, c1, c2, f0, e0, l0):
    from pyseobnr.generate_waveform import generate_modes_opt
    t, modos = generate_modes_opt(q, c1, c2, np.pi * f0, eccentricity=e0, rel_anomaly=l0, approximant="SEOBNRv5EHM")
    h = {}
    for chave, v in modos.items():
        l, m = (int(x) for x in chave.split(","))
        h[(l, m)] = np.asarray(v)
        h[(l, -m)] = (-1) ** l * np.conj(h[(l, m)])
    return np.asarray(t), h


def vet(t, h, q, x0):
    eta = q / (1 + q) ** 2
    return B.vetor(E.memorias_janela(t, h, E.LISTA, E.calc(), eta, x0)[0])[0]


def vet_global(q, c1, c2, M, e0, l0):
    f0 = M * Dt.MSUN_S * E.F_FIS
    t, h = gerar_l0(q, c1, c2, f0, e0, l0)
    v = vet(t, h, q, (np.pi * f0) ** (2 / 3))
    del t, h
    return v


def subjanelas(q, c1, c2, M, e0, l0, Ts):
    """Memorias em [t_pico - T, fim] para cada T, e no inicio [t0, t0 + 2 T_orb]."""
    f0 = M * Dt.MSUN_S * E.F_FIS
    x0 = (np.pi * f0) ** (2 / 3)
    t, h = gerar_l0(q, c1, c2, f0, e0, l0)
    ip = np.argmax(np.abs(h[(2, 2)]))
    s = t - t[ip]
    out = {"cheia": vet(t, h, q, x0), "duracao": s[-1] - s[0]}
    for T in Ts:
        i0 = np.searchsorted(s, -T)
        out[T] = vet(t[i0:], {k: v[i0:] for k, v in h.items()}, q, x0)
    T_orb = 2.0 / f0
    i1 = np.searchsorted(t - t[0], 2 * T_orb)
    out["inicio"] = vet(t[:i1], {k: v[:i1] for k, v in h.items()}, q, x0)
    del t, h
    return out


if __name__ == "__main__":
    t0 = time.time()
    # ---------- a) ----------
    log("a) item 4: M = 65, q = 1.2, chi = (+0.3, -0.2); memorias globais relativas ao circular (desl20, spin30, giro10)")
    v0 = vet_global(1.2, 0.3, -0.2, 65.0, 0.0, 0.0)
    for e0 in (0.1, 0.2):
        for l0 in (0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi):
            v = vet_global(1.2, 0.3, -0.2, 65.0, e0, l0)
            d = (v - v0) / np.abs(v0)
            log("   e0 = %.1f l0 = %.2f pi: %s" % (e0, l0 / np.pi, " ".join("%s %+.4f" % (NOMES[i], d[i]) for i in IDX)))
    # ---------- b) ----------
    log()
    DADOS = json.load(open(os.path.join(RAIZ, "resultados", "exp12_pares.json")))
    p = [x for x in DADOS["pares"] if x["e0"] == 0.2 and x["qB"] == 2.0][0]
    Ts = (8000.0, 4000.0, 2000.0, 1000.0, 500.0, 200.0, 100.0, 50.0)
    S0 = subjanelas(2.0, p["c1"], 0.0, p["M"], 0.2, 0.0, Ts)
    S1 = subjanelas(2.0, p["c1"], 0.0, p["M"], 0.2, np.pi, Ts)
    log("b) item 5: B (e0 = 0.2, q_B = 2, chi1 = %.4f, M = %.2f): l0 = pi x l0 = 0 (duracao %.1f x %.1f M)"
        % (p["c1"], p["M"], S1["duracao"], S0["duracao"]))
    log("   diferenca (l0 = pi) - (l0 = 0) da memoria acumulada na subjanela, em unidades do valor da janela cheia com l0 = 0")
    ref = S0["cheia"]
    def linha(rot, a, b):
        d = (b - a) / np.abs(ref)
        return "   %-26s %s" % (rot, " ".join("%s %+.2e" % (NOMES[i], d[i]) for i in IDX))
    log(linha("janela cheia", S0["cheia"], S1["cheia"]))
    for T in Ts:
        log(linha("[t_pico - %4.0f M, fim]" % T, S0[T], S1[T]))
    log(linha("inicio [t0, t0 + 2 T_orb]", S0["inicio"], S1["inicio"]))
    log("   fracao da janela cheia acumulada em [t_pico - 500 M, fim] (l0 = 0): %s"
        % " ".join("%s %.3f" % (NOMES[i], S0[500.0][i] / S0["cheia"][i]) for i in IDX))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "rev_R4v_anomalia.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
