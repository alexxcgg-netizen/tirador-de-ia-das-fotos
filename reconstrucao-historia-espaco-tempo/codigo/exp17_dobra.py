"""Experimento 17 (L02): a borda interior da fibra T0 e uma dobra? Continuacao exata em chi2_B a q_B fixo.

Para q_B em (1.5, 2.0, 3.0): parte da solucao exata da folha principal em chi2_B = 0 (exp17_fibra.json) e diminui chi2_B
em passos de 0.02, resolvendo (iota, chi1, M) exatamente (exp17_resolver) a partir da solucao anterior. Mede o menor
valor singular do jacobiano 3 x 3 dos residuos (spin, CM, giro relativos) em (iota, chi1, M); numa dobra ele vai a
zero e d chi1 / d chi2 diverge. No ultimo ponto com solucao procura a segunda solucao partindo do outro lado
(chi1 + 0.05). Para quando o residuo nao cai abaixo de 1e-8 ou chi1 atinge 0.8.
Saidas: resultados/exp17_dobra.txt
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


def smin(rs, x):
    Jm = rs.jac(np.array(x))
    return np.linalg.svd(Jm * np.array([0.1, 0.1, 10.0])[None, :], compute_uv=False)


if __name__ == "__main__":
    d = json.load(open(os.path.join(RES, "exp17_fibra.json")))
    alvo0 = dict(zip(R.TIPOS, d["alvo_T0"]))
    for qB in (1.5, 2.0, 3.0):
        reg = d["pontos"]["%.2f|%+.2f" % (qB, -0.0)]
        ex = [s["exato"] for s in reg["T0"] if "exato" in s and s["exato"]["res"] < 1e-8]
        if not ex:
            log("q_B %.2f: sem solucao em chi2_B = 0" % qB)
            continue
        s0 = min(ex, key=lambda x: x["chi1"])
        x = (s0["iota"], s0["chi1"], s0["M"])
        log("")
        log("q_B = %.2f: chi2_B, iota (graus), chi1, M, D, residuo, sigma(J 3x3, escala iota 0.1, chi1 0.1, M 10)" % qB)
        ult = None
        for k in range(0, 60):
            c2 = -0.02 * k
            rs = R.Resolvedor(alvo0, qB, c2, "T0")
            s = rs.resolver(x, max_nfev=20)
            if s["res"] > 1e-8 or s["no_limite"]:
                log("  chi2_B %+.3f: sem solucao a partir da anterior (residuo %.1e, chi1 %.4f, no limite %s)"
                    % (c2, s["res"], s["chi1"], s["no_limite"]))
                break
            sv = smin(rs, (s["iota"], s["chi1"], s["M"]))
            log("  %+.3f  %.4f  %+.5f  %.4f  %.3f  %.1e  %s" % (c2, np.degrees(s["iota"]), s["chi1"], s["M"], s["D"], s["res"],
                                                             np.array2string(sv, precision=3)))
            ult = (c2, s)
            x = (s["iota"], s["chi1"], s["M"])
        if ult is not None:
            c2, s = ult
            rs = R.Resolvedor(alvo0, qB, c2, "T0")
            for dchi in (0.03, 0.06, 0.1):
                s2 = rs.resolver((s["iota"] - np.radians(2.0), min(s["chi1"] + dchi, 0.7999), s["M"]), max_nfev=25)
                log("  segunda solucao em chi2_B %+.3f partindo de chi1 + %.2f: iota %.4f chi1 %+.5f M %.4f D %.3f residuo %.1e%s"
                    % (c2, dchi, np.degrees(s2["iota"]), s2["chi1"], s2["M"], s2["D"], s2["res"], " NO LIMITE" if s2["no_limite"] else ""))
    with open(os.path.join(RES, "exp17_dobra.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
