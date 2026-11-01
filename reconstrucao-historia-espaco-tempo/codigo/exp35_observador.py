"""exp35 (L10, tarefa 4) - um observador de uma binaria precessante: quantos numeros de memoria e quantos parametros.

No observador (iota, phi) do referencial da fonte (z = L em t_i, x = n), base de polarizacao (theta, phi) girada
de psi (angulo de polarizacao):
  desl_+ , desl_x          : Re e -Im de e^{2 i psi} sum_lm DeltaJ_lm (-2)Y_lm      (deformacao de memoria)
  int_+  , int_x           : Re e -Im de e^{2 i psi} sum_lm (cm_lm + spin_lm) (-2)Y_lm  (int h du da memoria: CM + spin;
                             num ponto as partes E e B nao se separam)
  giro                     : sum giro_lm Y_lm (escalar; nao mensuravel por interferometros, item 5 da revisao)
Um interferometro so mede F_+ h_+ + F_x h_x: com F desconhecidos, um numero por tipo (desl e int).

Jacobianos em relacao a (q, chiA, chiB) [7] + (iota, phi, psi) [3], em J1, J2, J5 (exp33_jacobiano) e no alinhado
J0, para iota = 50 graus, phi = 0.3; varredura do ceu (12 x 24) do menor valor singular do jacobiano 4 x 10.
Razao |x|/|+| no ceu para desl e int (precessante contra alinhado).
Saida: resultados/exp35_observador.txt, figuras/e35_observador.png
"""
import os
import time

import numpy as np

import exp33_comum as C
import exp33_jacobiano as EJ
from harmonicos import sYlm

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
F0 = C.F0_PADRAO
linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def mem_de(p):
    return EJ.avaliar(np.asarray(p, float))[2]


def obs(mem, iota, phi, psi):
    """[desl_+, desl_x, int_+, int_x, giro] no observador."""
    def soma(d, s=-2):
        return sum(c * complex(sYlm(s, l, m, iota, phi)) for (l, m), c in d.items() if l >= abs(s))
    rot = np.exp(2j * psi)
    D = rot * soma(mem["deslocamento"])
    I = rot * (soma(mem["cm"]) + soma(mem["spin"]))
    G = soma(mem["giroscopica"], 0)
    return np.array([D.real, -D.imag, I.real, -I.imag, G.real])


def derivadas_multipolos(p0, hh=1e-5):
    """d mem / d p_k (dicts complexos) por diferencas centrais."""
    out = []
    for k in range(7):
        e = np.zeros(7)
        e[k] = hh
        mp, mm = mem_de(p0 + e), mem_de(p0 - e)
        out.append({t: {lm: (mp[t][lm] - mm[t].get(lm, 0j)) / (2 * hh) for lm in mp[t]} for t in mp})
    return out


def jac_obs(mem0, dmem, iota, phi, psi, ha=1e-6):
    cols = [obs(d, iota, phi, psi) - 0 for d in dmem]          # linear nos multipolos
    for k, (a, b, c) in enumerate(((ha, 0, 0), (0, ha, 0), (0, 0, ha))):
        cols.append((obs(mem0, iota + a, phi + b, psi + c) - obs(mem0, iota - a, phi - b, psi - c)) / (2 * ha))
    return np.array(cols).T


def fmt(s):
    return " ".join("%.2e" % x for x in s)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    log("exp35_observador: numeros de memoria num observador e parametros (NRSur7dq4, nivel A, f0 = %.4f)" % F0)
    log("parametros: q, chiA(3), chiB(3), iota, phi, psi (10) ; numeros: desl_+, desl_x, int_+, int_x [, giro]")
    iota, phi, psi = np.radians(50.0), 0.3, 0.0
    mapas = {}
    for nome in ("J0", "J1", "J2", "J5"):
        q, cA, cB = EJ.PONTOS[nome]
        p0 = np.array([q, *cA, *cB], float)
        mem0 = mem_de(p0)
        dmem = derivadas_multipolos(p0)
        o = obs(mem0, iota, phi, psi)
        J = jac_obs(mem0, dmem, iota, phi, psi)
        log("")
        log("=== %s (q %.2f chiA %s chiB %s), iota 50 graus, phi 0.3, psi 0" % (nome, q, cA, cB))
        log("  valores: desl_+ %.3e desl_x %.3e int_+ %.3e int_x %.3e giro %.3e (adimensionais: r h/M, r int h/M^2,"
            " r^2 Phi/M^2)" % tuple(o))
        for rot, idx_l, idx_c in (("4 x 10 (desl, int; todos os parametros)", [0, 1, 2, 3], list(range(10))),
                                  ("5 x 10 (com giro)", [0, 1, 2, 3, 4], list(range(10))),
                                  ("4 x 7 (so intrinsecos; iota, phi, psi fixos)", [0, 1, 2, 3], list(range(7))),
                                  ("2 x 7 (so desl_+, int_+: a polarizacao x ignorada)", [0, 2], list(range(7))),
                                  ("4 x 3 (so angulos)", [0, 1, 2, 3], [7, 8, 9])):
            esc = np.array([np.hypot(o[0], o[1])] * 2 + [np.hypot(o[2], o[3])] * 2 + [abs(o[4])])
            Jn = J[np.ix_(idx_l, idx_c)] / esc[idx_l][:, None]   # relativo ao modulo de cada tipo
            s = np.linalg.svd(Jn, compute_uv=False)
            log("  %-50s valores singulares (linhas / |tipo|): %s" % (rot, fmt(s)))
        # um detector: F_+ h_+ + F_x h_x para cada tipo, F desconhecido -> 2 numeros
        log("  um interferometro: 2 numeros (F_+ desl_+ + F_x desl_x, F_+ int_+ + F_x int_x); com F_+, F_x desconhecidos"
            " a razao entre eles fixa so (F_x/F_+) se as razoes |x|/|+| dos dois tipos diferirem")
        # varredura do ceu
        th = np.radians(np.linspace(5, 175, 12))
        ph = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        smin = np.zeros((len(th), len(ph)))
        rD = np.zeros_like(smin)
        rI = np.zeros_like(smin)
        for i, a in enumerate(th):
            for j, b in enumerate(ph):
                oo = obs(mem0, a, b, 0.0)
                JJ = jac_obs(mem0, dmem, a, b, 0.0)[:4] / np.maximum(np.abs(oo[:4]).max(), 1e-300)
                smin[i, j] = np.linalg.svd(JJ, compute_uv=False)[-1]
                rD[i, j] = abs(oo[1]) / abs(oo[0])
                rI[i, j] = abs(oo[3]) / abs(oo[2])
        log("  ceu (12 x 24): menor valor singular do 4 x 10 (normalizado pelo maior |valor|): min %.2e, mediana %.2e,"
            " max %.2e" % (smin.min(), np.median(smin), smin.max()))
        log("  razao |desl_x|/|desl_+|: mediana %.3f, max %.3f ; razao |int_x|/|int_+|: mediana %.3f, max %.3f" % (
            np.median(rD), rD.max(), np.median(rI), rI.max()))
        mapas[nome] = (th, ph, smin, rD)
        log("  (%.0f s)" % (time.time() - T0))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for a, nome in zip(ax, ("J0", "J1")):
        th, ph, smin, rD = mapas[nome]
        a.set_facecolor("#fcfcfb")
        im = a.pcolormesh(np.degrees(ph), np.degrees(th), np.log10(rD), cmap="viridis", shading="auto")
        a.set_xlabel("phi do observador (graus)", color="#52514e")
        a.set_ylabel("iota (graus)", color="#52514e")
        a.set_title("%s: log10 |desl_x| / |desl_+|" % ("alinhado J0" if nome == "J0" else "precessante J1"),
                    color="#52514e", fontsize=10)
        fig.colorbar(im, ax=a)
        a.tick_params(colors="#52514e")
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e35_observador.png"), dpi=130, facecolor="#fcfcfb")
    with open(os.path.join(RAIZ, "resultados", "exp35_observador.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    main()
