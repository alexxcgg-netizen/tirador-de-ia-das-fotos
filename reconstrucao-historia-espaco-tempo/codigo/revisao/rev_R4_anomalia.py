"""Revisor R4, tarefa 2: a anomalia relativistica inicial l0 como parametro extra (SEOBNRv5EHM, nivel A).

Par: A circular do exp12 x B (e0 = 0.2, q_B = 2, chi2_B = 0) de resultados/exp12_pares.json, construido com l0 = 0.
  a) memorias de B com l0 = 0, pi/2, pi, 3pi/2 (resto fixo): variacao em relacao a l0 = 0 e diferenca ao alvo A;
  b) varredura fina l0 em [0, 2 pi) (16 pontos) para ver a forma da dependencia;
  c) para cada l0 != 0, resolve de novo (iota_B, chi1_B, M_B) com D_B eliminado pelo deslocamento, como no exp12,
     partindo da solucao de l0 = 0; reavalia a solucao sem cache;
  d) jacobiano 4 x 8 das quatro memorias (log) em relacao a (M, q, chi1, chi2, e0, l0, iota, D) no ponto B,
     diferencas centrais com passo grande (acima do tremor ~1e-5): valores singulares (posto = 4 => a familia
     tem dimensao 8 - 4 = 4 com l0, 3 sem l0 nos 7 parametros restantes).
Saida: resultados/revisao/rev_R4_anomalia.txt e .json
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


DADOS = json.load(open(os.path.join(C.RAIZ, "resultados", "exp12_pares.json")))
ALVO = DADOS["alvo"]
p = [x for x in DADOS["pares"] if x["e0"] == 0.2 and x["qB"] == 2.0][0]
B0 = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"], e=p["e0"], l0=0.0)
TIP = ("deslocamento", "spin", "cm", "giroscopica")


def fmt(d):
    return " ".join("%s %+.2e" % (k[:4], d[k]) for k in TIP)


def resolver(l0, x0):
    """(iota, chi1, M) com D eliminado, l0 fixo; mesmos limites e opcoes do exp12."""
    def montar(x):
        iota, c1, M = x
        par = dict(B0, M=M, c1=c1, iota=iota, D=1.0, l0=l0)
        v1, _ = C.fisicos(par)
        par["D"] = v1["deslocamento"] / ALVO["deslocamento"]
        return par

    def res(x):
        v, _ = C.fisicos(montar(x))
        return np.array([(v[k] - ALVO[k]) / abs(ALVO[k]) for k in ("spin", "cm", "giroscopica")])

    r = least_squares(res, x0, bounds=([0.05, -0.8, 35.0], [np.pi - 0.05, 0.8, 250.0]),
                      diff_step=1e-3, xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=150)
    return montar(r.x), float(np.max(np.abs(r.fun))), r.nfev


if __name__ == "__main__":
    t0 = time.time()
    out = {}
    log("Tarefa 2: anomalia relativistica inicial l0 (rel_anomaly) no par A circular x B (e0 = 0.2, q_B = 2) do exp12")
    log("  B (l0 = 0): M = %.4f, chi1 = %+.4f, D = %.2f Mpc, iota = %.2f graus" % (B0["M"], B0["c1"], B0["D"], np.degrees(B0["iota"])))
    log()
    log("a) memorias de B com l0 variando (resto fixo)")
    v0, _ = C.fisicos(B0, usar_cache=False)
    out["a"] = {}
    for l0 in (0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi):
        v, aux = C.fisicos(dict(B0, l0=l0), usar_cache=False)
        dl = C.dif_rel(v, v0)
        da = C.dif_rel(v, ALVO)
        log("  l0 = %4.2f pi: variacao em relacao a l0 = 0: max %.2e [%s] | B - A: max %.2e [%s]"
            % (l0 / np.pi, C.maxabs(dl), fmt(dl), C.maxabs(da), fmt(da)))
        out["a"]["%.4f" % l0] = dict(v=v, var_l0=dl, dif_A=da)
    log()
    log("b) varredura fina em l0 (16 pontos): variacao relativa em relacao a l0 = 0")
    grade = np.arange(16) * 2 * np.pi / 16
    serie = []
    for l0 in grade:
        v, _ = C.fisicos(dict(B0, l0=float(l0)), usar_cache=False)
        serie.append([C.dif_rel(v, v0)[k] for k in TIP])
    serie = np.array(serie)
    for k, nome in enumerate(TIP):
        s = serie[:, k]
        # ajuste a0 + a1 cos l0 + b1 sin l0 + a2 cos 2l0 + b2 sin 2l0
        X = np.c_[np.ones_like(grade), np.cos(grade), np.sin(grade), np.cos(2 * grade), np.sin(2 * grade)]
        cf, *_ = np.linalg.lstsq(X, s, rcond=None)
        resid = s - X @ cf
        log("  %-12s amplitude pico a pico %.2e ; harmonico 1: %.2e ; harmonico 2: %.2e ; resto (rms) %.1e"
            % (nome, s.max() - s.min(), np.hypot(cf[1], cf[2]), np.hypot(cf[3], cf[4]), np.sqrt(np.mean(resid ** 2))))
    out["b"] = dict(l0=grade.tolist(), var=serie.tolist())
    log()
    log("c) resolve de novo (iota_B, chi1_B, M_B; D_B pelo deslocamento) para cada l0, partindo da solucao de l0 = 0")
    out["c"] = {}
    for l0 in (0.5 * np.pi, np.pi, 1.5 * np.pi):
        C._cache.clear()
        par, r, nfev = resolver(l0, (B0["iota"], B0["c1"], B0["M"]))
        v, _ = C.fisicos(par, usar_cache=False)
        d = C.dif_rel(v, ALVO)
        log("  l0 = %4.2f pi: M_B = %.4f (%+.2e), chi1_B = %+.5f (%+.1e), iota_B = %.3f graus (%+.1e), D_B = %.2f Mpc (%+.1e) | residuo do otimizador %.1e (%d aval.), reavaliado %.2e [%s]"
            % (l0 / np.pi, par["M"], par["M"] / B0["M"] - 1, par["c1"], par["c1"] - B0["c1"], np.degrees(par["iota"]),
               np.degrees(par["iota"] - B0["iota"]), par["D"], par["D"] / B0["D"] - 1, r, nfev, C.maxabs(d), fmt(d)))
        out["c"]["%.4f" % l0] = dict(par=par, residuo=r, reaval=d)
    C._cache.clear()
    log()
    log("d) jacobiano d log|m_k| / d p_j no ponto B (diferencas centrais), valores singulares")
    nomes_p = ["M", "q", "c1", "c2", "e", "l0", "iota", "D"]
    passos = dict(M=0.05 * B0["M"] * 1e-2, q=0.01, c1=0.01, c2=0.01, e=0.01, l0=0.2, iota=0.01, D=0.01 * B0["D"])
    J = np.zeros((4, 8))
    for j, nome in enumerate(nomes_p):
        h = passos[nome]
        vp, _ = C.fisicos(dict(B0, **{nome: B0[nome] + h}), usar_cache=False)
        vm, _ = C.fisicos(dict(B0, **{nome: B0[nome] - h}), usar_cache=False)
        for i, k in enumerate(TIP):
            J[i, j] = (np.log(abs(vp[k])) - np.log(abs(vm[k]))) / (2 * h)
    for i, k in enumerate(TIP):
        log("  %-12s " % k + " ".join("%s %+.3e" % (n, J[i, j]) for j, n in enumerate(nomes_p)))
    # escala dos parametros para valores singulares comparaveis: passo natural de cada um
    esc = np.array([B0["M"] * 0.01, 0.1, 0.1, 0.1, 0.1, 1.0, 0.1, B0["D"] * 0.01])
    Js = J * esc
    sv = np.linalg.svd(Js, compute_uv=False)
    sv7 = np.linalg.svd(np.delete(Js, 5, axis=1), compute_uv=False)
    log("  valores singulares (colunas escaladas por M/100, 0.1, 0.1, 0.1, 0.1, 1 rad, 0.1 rad, D/100): com l0 %s ; sem l0 %s"
        % (np.array2string(sv, precision=3), np.array2string(sv7, precision=3)))
    # tremor do jacobiano: o mesmo com passos 10x menores na coluna l0
    vp, _ = C.fisicos(dict(B0, l0=0.02), usar_cache=False)
    vm, _ = C.fisicos(dict(B0, l0=-0.02), usar_cache=False)
    col = [(np.log(abs(vp[k])) - np.log(abs(vm[k]))) / 0.04 for k in TIP]
    log("  coluna l0 com passo 0.02 (10x menor): " + " ".join("%+.3e" % x for x in col))
    out["d"] = dict(J=J.tolist(), nomes=nomes_p, sv=sv.tolist(), sv_sem_l0=sv7.tolist())
    log()
    log("avisos do pyseobnr: %d %s" % (len(C.COLETOR.msgs), " || ".join(C.COLETOR.msgs[:3])))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(C.RES, "rev_R4_anomalia.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(C.RES, "rev_R4_anomalia.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
