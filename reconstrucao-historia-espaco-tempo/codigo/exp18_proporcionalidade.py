"""Experimento 18 (tarefa 5, reducao (2,2)): com so (2,+-2) as memorias sao funcoes de tres integrais no tempo.

Para h = h22 Y22 + h2-2 Y2-2, h2-2 = conj(h22) (spins alinhados), os multipolos m = 0 de qualquer bilinear em (h, hdot)
so envolvem |hdot22|^2, |h22|^2, Re(conj(h22) hdot22) = (1/2) d|h22|^2/dt e Im(conj(h22) hdot22). Integrando na janela:
  E = int |hdot22|^2 du,   H = int Im(conj(h22) hdot22) du,   B = |h22|^2 (borda: t_i e fim).
Previsao [D]: J20, J40 proporcionais a E; S30, G10, G30 proporcionais a H; parte nula de K20 proporcional a B (borda)
com constantes universais (coeficientes de Gaunt). Logo spin e giroscopica carregam a MESMA informacao intrinseca
(spin/giro = constante x D x forma angular) e o jacobiano intrinseco (D, iota fixos) tem posto <= 3.
Teste: razoes J20/E, S30/H, G10/H, G30/H, (K20 - ordinaria)/B para varios (q, chi1, chi2, M).
Saida: resultados/exp18_proporcionalidade.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402
import observaveis as O                                  # noqa: E402
from harmonicos import Dfrak                             # noqa: E402

SAIDA = os.path.join(AQUI, "..", "resultados", "exp18_proporcionalidade.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    log("Modelo so (2,+-2), nivel A, janela desde 10 Hz: razoes que deveriam ser universais")
    log("%-26s %12s %12s %12s %12s %12s" % ("(q, chi1, chi2, M)", "J20/E", "S30/H", "G10/H", "G30/H", "Knula20/B"))
    for (q, c1, c2, M) in [(1.2, 0.3, -0.2, 65.0), (2.0, 0.0, 0.0, 65.0), (3.0, 0.6, 0.0, 65.0), (1.2, -0.6, 0.6, 65.0),
                           (4.0, 0.3, 0.3, 65.0), (1.5, 0.0, 0.0, 120.0), (1.0, 0.6, 0.6, 30.0)]:
        r = C.memorias_varias(q, c1, c2, [M], media=False, modos=[(2, 2), (2, -2)])[0]
        mem, aux = r["mem_ti"], r["aux"]
        # integrais diretas no tempo com a mesma quadratura
        t, h, ti = O.gerar_janela(q, c1, c2, M, 10.0)
        h22 = h[(2, 2)]
        hd = O.derivada(h22[:, None], t[1] - t[0], 8)[:, 0]
        w = O.pesos_janela(t, ti)
        E = float(np.sum(w * np.abs(hd) ** 2))
        H = float(np.sum(w * np.imag(np.conj(h22) * hd)))
        Bb = float(np.abs(h22[-1]) ** 2 - np.abs(O._interp_em(t, h22, ti)) ** 2)
        del t, h, h22, hd
        Mf = aux["M_f"]
        knula = mem["cm"][(2, 0)].real - (-1.5 * Mf * mem["deslocamento"][(2, 0)].real / Dfrak(2))
        log("%-26s %12.6e %12.6e %12.6e %12.6e %12.6e" % ("(%.1f, %+.1f, %+.1f, %.0f)" % (q, c1, c2, M),
                                                           mem["deslocamento"][(2, 0)].real / E, mem["spin"][(3, 0)].imag / H,
                                                           mem["giroscopica"][(1, 0)].real / H, mem["giroscopica"][(3, 0)].real / H,
                                                           knula / Bb))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(linhas) + "\n")
