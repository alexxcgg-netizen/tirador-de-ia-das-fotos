"""Revisao R1: posto do jacobiano das quatro memorias no observador e anatomia da memoria de CM.

Itens (secao 2.2 e 1.2 do 07; nivel A, NRHybSur3dq8_CCE, janela desde 10 Hz, como no exp07):
  J1  jacobiano dF/dp, p = (ln M, q, chi1, chi2, ln D, iota), F = (desl, spin, CM, giro) do sistema A,
      para varias inclinacoes; valores singulares (linhas normalizadas pelo valor em iota = 50 graus).
  J2  paridade: F(pi - iota) contra F(iota) com as memorias do proprio codigo.
  J3  memoria de CM: parte ordinaria -(3/2) M_f Dfrak^-1 Delta Phi_E contra parte nula, por l, e a razao
      CM / (M Delta h_+) contra -M_f/2 (que seria exata se so houvesse a parte ordinaria em l = 2);
      o mesmo para os pares do exp07.
So as memorias (dicionarios pequenos) ficam na memoria; a forma de onda e descartada a cada ponto.
Saida: resultados/revisao/rev_R1_jacobiano.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
from harmonicos import Dfrak, sYlm                       # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1_jacobiano.txt")
linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


F_FIS = 10.0
A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0)
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")


def mems(q, c1, c2, M, f_fis=F_FIS):
    mem, aux, t, h = B.memorias_fisicas(q, c1, c2, M, f_fis, nivel="A")
    del t, h
    return mem, dict(M_f=aux["M_f"], E_rad=aux["E_rad"], v=float(np.linalg.norm(aux["v_recuo"])))


def vetorF(mem, iota, M, D):
    v = B.valores_fisicos(mem, iota, M, D)
    return np.array([v[k] for k in TIPOS])


# ---------------- pontos do jacobiano intrinseco
passos = {"lnM": 1e-4, "q": 1e-3, "c1": 1e-3, "c2": 1e-3}
base_mem, base_aux = mems(A["q"], A["c1"], A["c2"], A["M"])
pert = {}
for nome, h in passos.items():
    for sgn in (+1, -1):
        p = dict(A)
        if nome == "lnM":
            p["M"] = A["M"] * np.exp(sgn * h)
        else:
            p[nome] = A[nome] + sgn * h
        pert[(nome, sgn)] = (p, mems(p["q"], p["c1"], p["c2"], p["M"])[0])
log("pontos do jacobiano calculados (%.0f s)" % (time.time() - T0))


def jacobiano(iota):
    cols = []
    for nome, h in passos.items():
        pp, mp = pert[(nome, +1)]
        pm, mm = pert[(nome, -1)]
        cols.append((vetorF(mp, iota, pp["M"], A["D"]) - vetorF(mm, iota, pm["M"], A["D"])) / (2 * h))
    F0 = vetorF(base_mem, iota, A["M"], A["D"])
    cols.append(np.array([-1.0, -1.0, -1.0, -2.0]) * F0)                     # d/d ln D
    di = 1e-5
    cols.append((vetorF(base_mem, iota + di, A["M"], A["D"]) - vetorF(base_mem, iota - di, A["M"], A["D"])) / (2 * di))
    return np.array(cols).T, F0


escala = np.abs(vetorF(base_mem, np.radians(50.0), A["M"], A["D"]))
log("")
log("J1 jacobiano 4 x 6 (linhas / |F(50 graus)|), colunas (ln M, q, chi1, chi2, ln D, iota)")
for graus in (50.0, 70.0, 85.0, 89.0, 89.9, 90.0, 30.0, 10.0, 2.0, 0.5, 0.0):
    J, F0 = jacobiano(np.radians(graus))
    Jn = J / escala[:, None]
    sv = np.linalg.svd(Jn, compute_uv=False)
    # posto com linhas normalizadas pela propria norma (o posto nao depende da escala das linhas)
    nr = np.linalg.norm(J, axis=1)
    Jr = J / np.where(nr > 0, nr, 1)[:, None]
    svr = np.linalg.svd(Jr, compute_uv=False)
    log("  iota = %5.1f graus: F/|F(50)| = %s | sv = %s | sv (linhas unitarias) = %s"
        % (graus, np.array2string(F0 / escala, precision=3), np.array2string(sv, precision=3),
           np.array2string(svr, precision=3)))
    if graus == 50.0:
        U, S, Vt = np.linalg.svd(Jn)
        log("     direcao de menor sv no espaco (desl, spin, CM, giro): %s" % np.array2string(U[:, -1], precision=3))
        Jint = Jn[:, :4]
        Ui, Si, Vti = np.linalg.svd(Jint)
        log("     so intrinsecos (ln M, q, chi1, chi2): sv = %s ; direcao quase nula = %s"
            % (np.array2string(Si, precision=3), np.array2string(Vti[-1], precision=3)))
        cosang = abs(np.dot(Jn[0], Jn[2])) / (np.linalg.norm(Jn[0]) * np.linalg.norm(Jn[2]))
        log("     cos do angulo entre as linhas desl e CM (relativas) = %.6f" % cosang)

# ---------------- duas janelas
log("")
log("J4 duas janelas (10 Hz e 20 Hz): jacobiano relativo 8 x 6 em iota = 50 graus")
base20 = mems(A["q"], A["c1"], A["c2"], A["M"], 20.0)[0]
pert20 = {}
for (nome, sgn), (p, _) in pert.items():
    pert20[(nome, sgn)] = mems(p["q"], p["c1"], p["c2"], p["M"], 20.0)[0]
iota = np.radians(50.0)


def jac_rel(bm, pt, iota):
    cols = []
    for nome, h in passos.items():
        pp, pm = pert[(nome, +1)][0], pert[(nome, -1)][0]
        cols.append((vetorF(pt[(nome, +1)], iota, pp["M"], A["D"]) - vetorF(pt[(nome, -1)], iota, pm["M"], A["D"])) / (2 * h))
    F0 = vetorF(bm, iota, A["M"], A["D"])
    cols.append(np.array([-1.0, -1.0, -1.0, -2.0]) * F0)
    di = 1e-5
    cols.append((vetorF(bm, iota + di, A["M"], A["D"]) - vetorF(bm, iota - di, A["M"], A["D"])) / (2 * di))
    return np.array(cols).T / np.abs(F0)[:, None], F0


J10, F10 = jac_rel(base_mem, {k: v[1] for k, v in pert.items()}, iota)
J20, F20 = jac_rel(base20, pert20, iota)
log("  F(20 Hz)/F(10 Hz) = %s" % np.array2string(F20 / F10, precision=5))
for nome, Jm in (("10 Hz (4 x 6)", J10), ("10 + 20 Hz (8 x 6)", np.vstack([J10, J20])),
                 ("10 Hz + diferencas 20-10 (8 x 6)", np.vstack([J10, J20 - J10]))):
    log("  %-32s sv = %s" % (nome, np.array2string(np.linalg.svd(Jm, compute_uv=False), precision=3)))
Jd = J20 - J10
log("  linhas da diferenca (desl, spin, CM, giro) x colunas (ln M, q, chi1, chi2, ln D, iota):")
for k, nm in enumerate(TIPOS):
    log("    %-13s %s" % (nm, np.array2string(Jd[k], precision=4)))

# ---------------- paridade
log("")
log("J2 paridade das memorias do codigo: F(pi - iota) / F(iota)")
for graus in (20.0, 50.0, 75.0):
    a = vetorF(base_mem, np.radians(graus), A["M"], A["D"])
    b = vetorF(base_mem, np.pi - np.radians(graus), A["M"], A["D"])
    log("  iota = %4.1f: %s" % (graus, np.array2string(b / a, precision=12)))

# ---------------- anatomia da memoria de CM
log("")
log("J3 memoria de CM no observador: parte ordinaria x parte nula (nivel A, deformacao, unidades de M)")


def anatomia(nome, mem, aux, iota, M):
    Mf = aux["M_f"]
    Y = {l: sYlm(-2, l, 0, iota, 0.0).real for l in (2, 3, 4, 5, 6, 7, 8)}
    d = sum(mem["deslocamento"][(l, 0)].real * Y[l] for l in (2, 4))
    ordl = {l: -1.5 * Mf * mem["deslocamento"][(l, 0)].real / Dfrak(l) * Y[l] for l in (2, 4)}
    tot = sum(mem["cm"][k].real * Y[k[0]] for k in mem["cm"] if k[0] <= 8)
    nul = tot - sum(ordl.values())
    log("  %-28s M_f/M = %.4f | CM/(M d) = %+.4f | ordinaria l=2: %+.4f, l=4: %+.4f | nula: %+.4f | -M_f/2 = %+.4f"
        % (nome, Mf, tot / d, ordl[2] / d, ordl[4] / d, nul / d, -Mf / 2))
    return tot / d * M, Mf * M


iA = np.radians(50.0)
rA = anatomia("A (q=1.2, 0.3/-0.2)", base_mem, base_aux, iA, A["M"])
with open(os.path.join(AQUI, "..", "..", "resultados", "exp07_pares.json")) as fh:
    pares = json.load(fh)["pares"]
for p in pares:
    if p["qB"] in (1.0, 2.0, 3.0) and (p["qB"], p["c2B"]) in ((1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (2.0, 0.5)):
        mB, auxB = mems(p["qB"], p["c1"], p["c2B"], p["M"])
        rB = anatomia("B (q=%.0f, %.3f/%.1f, M=%.2f)" % (p["qB"], p["c1"], p["c2B"], p["M"]), mB, auxB, p["iota"], p["M"])
        log("     M (CM/d) em M_sol: A %.3f, B %.3f ; M_f em M_sol: A %.2f, B %.2f" % (rA[0], rB[0], rA[1], rB[1]))
log("(%.0f s)" % (time.time() - T0))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(linhas) + "\n")
