"""Revisor R4, tarefa 2 (consequencia): l0 como incognita resolve os casos q_B = 1.2 do exp12?

No exp12 os casos q_B = 1.2, chi2_B = -0.2 ficaram com residuo 5.2e-4 (e0 = 0.1), 2.6e-4 (e0 = 0.2) e
1.15e-2 (e0 = 0.3, "sem solucao"), acima do piso ~1e-5. Aqui:
  i)  l0 = 0 fixo, de novo a partir da solucao gravada (mesmo metodo do exp12) -> o residuo e do otimizador?
  ii) l0 livre: incognitas (iota_B, chi1_B, M_B, l0), D_B pelo deslocamento; partidas l0 = pi/2, pi, 3pi/2.
Toda solucao e reavaliada sem cache. Saida: resultados/revisao/rev_R4_resolver_l0_e<e0>_chi<chi_max>.txt
Uso: python revisao/rev_R4_resolver_l0.py <e0> [chi_max]   (um caso por processo; chi_max = 0.8 como no exp12)
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402

DADOS = json.load(open(os.path.join(C.RAIZ, "resultados", "exp12_pares.json")))
ALVO = DADOS["alvo"]
TIP = ("deslocamento", "spin", "cm", "giroscopica")


CHI_MAX = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8


def resolver(base, x0, com_l0, max_nfev=80):
    def montar(x):
        par = dict(base, iota=x[0], c1=x[1], M=x[2], D=1.0, l0=(x[3] if com_l0 else 0.0))
        v1, _ = C.fisicos(par)
        par["D"] = v1["deslocamento"] / ALVO["deslocamento"]
        return par

    def res(x):
        v, _ = C.fisicos(montar(x))
        return np.array([(v[k] - ALVO[k]) / abs(ALVO[k]) for k in ("spin", "cm", "giroscopica")])

    lo, hi = [0.05, -0.8, 35.0], [np.pi - 0.05, CHI_MAX, 250.0]
    if com_l0:
        lo, hi = lo + [-np.pi], hi + [3 * np.pi]
    r = least_squares(res, x0, bounds=(lo, hi), diff_step=1e-3, xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=max_nfev)
    par = montar(r.x)
    v, _ = C.fisicos(par, usar_cache=False)
    d = C.dif_rel(v, ALVO)
    return par, float(np.max(np.abs(r.fun))), C.maxabs(d), d, r.nfev


if __name__ == "__main__":
    e0 = float(sys.argv[1])
    t0 = time.time()
    p = [x for x in DADOS["pares"] if x["e0"] == e0 and x["qB"] == 1.2][0]
    base = dict(M=p["M"], q=1.2, c1=p["c1"], c2=-0.2, D=p["D"], iota=p["iota"], e=e0, l0=0.0)
    linhas = ["caso e0 = %.1f, q_B = 1.2, chi2_B = -0.2, chi1 <= %.2f (residuo gravado no exp12 %.2e)" % (e0, CHI_MAX, p["residuo"])]
    par, r, rr, d, n = resolver(base, [p["iota"], p["c1"], p["M"]], False)
    linhas.append("  i)  l0 = 0, partindo da solucao gravada: residuo do otimizador %.2e, reavaliado %.2e (%d aval.) [%s] M %.3f chi1 %+.4f iota %.2f D %.1f"
                  % (r, rr, n, " ".join("%s %+.1e" % (k[:4], d[k]) for k in TIP), par["M"], par["c1"], np.degrees(par["iota"]), par["D"]))
    melhor = None
    for l0 in (0.5 * np.pi, np.pi, 1.5 * np.pi):
        C._cache.clear()
        par, r, rr, d, n = resolver(base, [p["iota"], p["c1"], p["M"], l0], True)
        linhas.append("  ii) l0 livre, partida l0 = %.2f pi: residuo %.2e, reavaliado %.2e (%d aval.) [%s] -> l0 = %.3f pi, M %.3f chi1 %+.4f iota %.2f D %.1f"
                      % (l0 / np.pi, r, rr, n, " ".join("%s %+.1e" % (k[:4], d[k]) for k in TIP), (par["l0"] % (2 * np.pi)) / np.pi,
                         par["M"], par["c1"], np.degrees(par["iota"]), par["D"]))
        if melhor is None or rr < melhor:
            melhor = rr
        if rr < 2e-5:
            break
    linhas.append("  melhor reavaliado com l0 livre: %.2e ; avisos do pyseobnr %d ; (%.0f s)" % (melhor, len(C.COLETOR.msgs), time.time() - t0))
    print("\n".join(linhas))
    with open(os.path.join(C.RES, "rev_R4_resolver_l0_e%.1f_chi%.2f.txt" % (e0, CHI_MAX)), "w") as f:
        f.write("\n".join(linhas) + "\n")
