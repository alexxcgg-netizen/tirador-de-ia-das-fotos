"""Verificador R3v: item 5 do revisor R3 (onde o h_20 do substituto excede a memoria nula do fluxo).

Para q = 1 e 8 (sem spin), janela M f0 = 0.004: desl20 de cada trecho pelo nivel A (Gram do trecho, derivada da onda
inteira) contra o incremento de h_20 do substituto no mesmo trecho. Trechos: PN [inicio, -3500], hibridizacao
[-3500, -2500], RN [-2500, -200], fim [-200, fim] (M do pico). Mais a janela do exp09 (M f0 = 0.006, inspiral ate -200 M).
Saida: resultados/revisao/rev_R3v_desl.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
from memorias import gram                               # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    dt = 0.25
    c_osc, _ = B.calculadoras()
    Losc = B.lista_osc()
    for f0 in (0.004, 0.006):
        for q in (1.0, 8.0):
            t, h = B.gerar(q, 0.0, 0.0, f0=f0, dt=dt)
            H = np.stack([h[k] for k in Losc], axis=1)
            Hd = B.derivada4(H, dt)
            tp = t[np.argmax(np.sum(np.abs(H) ** 2, axis=1))]
            h20 = h[(2, 0)].real
            log("M f0 = %.3f, q = %.0f (inicio %.0f M do pico)" % (f0, q, t[0] - tp))
            cortes = [-1e9, -3500, -2500, -200, 1e9]
            for a, b in zip(cortes[:-1], cortes[1:]):
                sel = np.where((t - tp > a) & (t - tp <= b))[0]
                if len(sel) < 10:
                    continue
                m = c_osc.memorias_gram(*gram(H[sel], Hd[sel], dt))
                dA = m["deslocamento"][(2, 0)].real
                i0, i1 = sel[0], sel[-1]
                dC = h20[i1] - (h20[i0 - 1] if i0 > 0 else h20[i0])
                log("   (%6.0f, %6.0f]: fluxo (A) = %.6e ; h20 (C) = %.6e ; C/A - 1 = %+.4f ; A - C = %+.2e"
                    % (max(a, t[0] - tp), min(b, t[-1] - tp), dA, dC, dC / dA - 1, dA - dC))
            del t, h, H, Hd
    with open(os.path.join(SAIDA, "rev_R3v_desl.txt"), "w") as fo:
        fo.write("\n".join(linhas) + "\n")
