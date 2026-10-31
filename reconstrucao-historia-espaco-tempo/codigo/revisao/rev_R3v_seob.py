"""Verificador R3v: itens 8 e 9 do revisor R3 (SEOBNRv5EHM, exp12).

 (9) ruido numerico: memorias de janela (nivel A, como no exp12) sob M -> M (1 + k 1e-6), k = 0..3, repeticao exata
     de k = 0, passo grande dM/M = 1e-3 (variacao suave esperada por 1e-6) e tolerancias do integrador mais apertadas.
 (8) valores ABSOLUTOS de janela (E_janela, desl20) com fusao, para dividir o peso absoluto do (2,0) do modelo PN.
Sistema: M = 65, q = 1.2, chi = (0.3, -0.2), 10 Hz; e0 = 0 e 0.2.
Saida: resultados/revisao/rev_R3v_seob.txt
"""
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
import exp12_excentricas_imr as E12                     # noqa: E402
from deteccao import MSUN_S                             # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao")
NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def mem(M, e0, settings=None):
    from pyseobnr.generate_waveform import generate_modes_opt
    f0 = M * MSUN_S * 10.0
    q, c1, c2 = 1.2, 0.3, -0.2
    t, modos = generate_modes_opt(q, c1, c2, np.pi * f0, eccentricity=e0, rel_anomaly=0.0,
                                  approximant="SEOBNRv5EHM", settings=settings)
    h = {}
    for chave, v in modos.items():
        l, m = (int(x) for x in chave.split(","))
        h[(l, m)] = np.asarray(v)
        h[(l, -m)] = (-1) ** l * np.conj(h[(l, m)])
    t = np.asarray(t)
    eta = q / (1 + q) ** 2
    out, aux = E12.memorias_janela(t, h, E12.LISTA, E12.calc(), eta, (np.pi * f0) ** (2 / 3))
    v = B.vetor(out)[0]
    del t, h, modos
    return v, aux


if __name__ == "__main__":
    t00 = time.time()
    for e0 in (0.0, 0.2):
        vs = [mem(65.0 * (1 + k * 1e-6), e0)[0] for k in range(4)]
        v0, aux0 = mem(65.0, e0)
        vg = mem(65.0 * (1 + 1e-3), e0)[0]
        vs = np.array(vs)
        dv = np.abs(np.diff(vs, axis=0)) / np.abs(vs[0])
        log("e0 = %.1f: E_janela = %.6e, desl20 = %.6e (unidades de M), spin30 = %.6e" % (e0, aux0["E_janela"], v0[0], v0[2]))
        log("  repeticao exata, max |dif| rel.: %.1e" % np.max(np.abs(v0 - vs[0]) / np.abs(vs[0])))
        log("  |v(k+1) - v(k)|/|v| com dM/M = 1e-6 (3 passos): "
            + "; ".join("%s %s" % (n, " ".join("%.1e" % x for x in dv[:, i])) for i, n in enumerate(NOMES)))
        log("  variacao suave esperada por 1e-6 (de dM/M = 1e-3): "
            + " ".join("%s %.1e" % (n, x) for n, x in zip(NOMES, np.abs(vg - vs[0]) / np.abs(vs[0]) / 1000)))
        try:
            vt = [mem(65.0 * (1 + k * 1e-6), e0, settings={"rtol": 1e-13, "atol": 1e-14})[0] for k in range(3)]
            vt = np.array(vt)
            dvt = np.abs(np.diff(vt, axis=0)) / np.abs(vt[0])
            log("  rtol = 1e-13, atol = 1e-14: |v(k+1)-v(k)|/|v|: "
                + "; ".join("%s %s" % (n, " ".join("%.1e" % x for x in dvt[:, i])) for i, n in enumerate(NOMES)))
            log("     diferenca para as tolerancias padrao (k = 0): "
                + " ".join("%s %.1e" % (n, x) for n, x in zip(NOMES, np.abs(vt[0] - vs[0]) / np.abs(vs[0]))))
        except Exception as ex:                          # noqa: BLE001
            log("  tolerancias apertadas: falhou (%s)" % ex)
        log("  (%.0f s)" % (time.time() - t00))
    with open(os.path.join(SAIDA, "rev_R3v_seob.txt"), "w") as fo:
        fo.write("\n".join(linhas) + "\n")
