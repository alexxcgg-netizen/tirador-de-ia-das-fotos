"""Experimento 18 (L01/L02, tarefa 5): reducao analitica para radiacao dominada pelo (2,2) e quanto ela explica do jacobiano.

So (2,+-2) como entrada (nivel A): cada memoria e uma projecao de |hdot_22|^2, Im(h_22 hdot_22*) e W(h_22) nas mesmas
formas angulares, logo as formas em iota ficam fixas (independentes da dinamica):
  desl  : J_40/J_20 = numero puro  ->  Delta h_+ ~ sin^2(iota) (17 + cos^2 iota)  [E: Favata 2009 eq. 4.5a]
  spin  : so l = 3                  ->  int h_x ~ sin^2(iota) cos(iota)            [E: Nichols 2017]
  CM    : l = 2, 4 (razao depende de lambda pela parte nula)
  giro  : l = 1, 3 (razao depende de lambda: helicidade x potencial de spin)
Compara o jacobiano T0 (ln M, q, chi1, chi2, ln D, iota) e o intrinseco (D, iota fixos) do modelo completo com o do
modelo so (2,2), em A e em alguns pontos: valores singulares, angulos principais entre os espacos nulos (dimensao 2)
e entre as direcoes quase nulas intrinsecas, ||J_22 - J||/||J||.
Saida: resultados/exp18_reducao.txt
"""
import os
import sys

import numpy as np
from scipy.linalg import subspace_angles

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402

SAIDA = os.path.join(AQUI, "..", "resultados", "exp18_reducao.txt")
linhas = []
D_MPC = 400.0
KD = np.array([1.0, 1.0, 1.0, 2.0])
SO22 = [(2, 2), (2, -2)]


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def F_de(mem, M, iota):
    return C.vetor_fisico(C.so_m0(mem), iota, 0.0, M, D_MPC)


def jac_T0(q, c1, c2, M, iota, modos=None, h=4e-3, hM=1e-4):
    """Jacobiano relativo T0 (4 x 6) por diferencas centrais com h e h/2 (devolve J(h/2) e |J(h) - J(h/2)|)."""
    Ms = [M, M * np.exp(hM), M * np.exp(-hM), M * np.exp(hM / 2), M * np.exp(-hM / 2)]
    rb = C.memorias_varias(q, c1, c2, Ms, media=False, modos=modos)
    F0 = F_de(rb[0]["mem_ti"], M, iota)
    cols = {1: [], 2: []}
    for k, fr in ((1, 1.0), (2, 0.5)):
        a, b = 2 * k - 1, 2 * k
        cols[k].append((F_de(rb[a]["mem_ti"], Ms[a], iota) - F_de(rb[b]["mem_ti"], Ms[b], iota)) / (2 * fr * hM))
    for d in range(3):
        for k, fr in ((1, 1.0), (2, 0.5)):
            pp, pm = [q, c1, c2], [q, c1, c2]
            pp[d] += fr * h
            pm[d] -= fr * h
            Fp = F_de(C.memorias_varias(*pp, [M], media=False, modos=modos)[0]["mem_ti"], M, iota)
            Fm = F_de(C.memorias_varias(*pm, [M], media=False, modos=modos)[0]["mem_ti"], M, iota)
            cols[k].append((Fp - Fm) / (2 * fr * h))
    e = 1e-6
    mem0 = rb[0]["mem_ti"]
    ci = (F_de(mem0, M, iota + e) - F_de(mem0, M, iota - e)) / (2 * e)
    J2 = np.array(cols[2] + [-KD * F0, ci]).T / np.abs(F0)[:, None]
    J1 = np.array(cols[1] + [-KD * F0, ci]).T / np.abs(F0)[:, None]
    return J2, np.abs(J1 - J2), F0, mem0


if __name__ == "__main__":
    np.set_printoptions(linewidth=150, precision=4)
    log("Reducao (2,2): formas angulares e jacobiano T0 (escala relativa; colunas ln M, q, chi1, chi2, ln D, iota)")
    pts = [(1.2, 0.3, -0.2), (2.0, 0.0, 0.0), (3.0, 0.6, 0.0), (1.2, -0.6, 0.6), (4.0, 0.3, 0.3)]
    io = np.radians(50.0)
    for (q, c1, c2) in pts:
        Jf, Ef, Ff, mf = jac_T0(q, c1, c2, 65.0, io)
        J2, E2, F2, m2 = jac_T0(q, c1, c2, 65.0, io, modos=SO22)
        log("")
        log("q = %.1f chi = (%+.1f, %+.1f), M = 65, iota = 50: F(so 22)/F(completo) - 1 = %s" % (q, c1, c2, F2 / Ff - 1))
        # formas angulares do modelo so (2,2)
        d = m2["deslocamento"]
        log("  so (2,2): desl J40/J20 = %.6f (numero puro sqrt(3)/180 = %.6f) ; J60/J20 = %.1e ; spin S50/S30 = %.1e ; CM K40/K20 = %.4f ;"
            " giro G30/G10 = %.4f" % (d[(4, 0)].real / d[(2, 0)].real, np.sqrt(3) / 180, abs(d[(6, 0)] / d[(2, 0)]),
                                     abs(m2["spin"][(5, 0)] / m2["spin"][(3, 0)]), m2["cm"][(4, 0)].real / m2["cm"][(2, 0)].real,
                                     m2["giroscopica"][(3, 0)].real / m2["giroscopica"][(1, 0)].real))
        log("  completo: desl J40/J20 = %.6f ; J60/J20 = %.1e ; spin S50/S30 = %.1e ; CM K40/K20 = %.4f ; giro G30/G10 = %.4f"
            % (mf["deslocamento"][(4, 0)].real / mf["deslocamento"][(2, 0)].real, abs(mf["deslocamento"][(6, 0)] / mf["deslocamento"][(2, 0)]),
               abs(mf["spin"][(5, 0)] / mf["spin"][(3, 0)]), mf["cm"][(4, 0)].real / mf["cm"][(2, 0)].real,
               mf["giroscopica"][(3, 0)].real / mf["giroscopica"][(1, 0)].real))
        for nome, Jm, Em in (("completo", Jf, Ef), ("so (2,2)", J2, E2)):
            sv = np.linalg.svd(Jm, compute_uv=False)
            svi = np.linalg.svd(Jm[:, :4], compute_uv=False)
            log("  %-9s sigma T0 = %s (tau %.1e) ; intrinseco = %s" % (nome, np.array2string(sv, precision=4), np.linalg.norm(Em),
                                                                      np.array2string(svi, precision=4)))
        log("  ||J22 - J||_F / ||J||_F = %.3f ; por linha: %s" % (np.linalg.norm(J2 - Jf) / np.linalg.norm(Jf),
                                                                  np.array2string(np.linalg.norm(J2 - Jf, axis=1) / np.linalg.norm(Jf, axis=1), precision=3)))
        Nf = np.linalg.svd(Jf)[2][4:].T
        N2 = np.linalg.svd(J2)[2][4:].T
        log("  angulos principais entre os espacos nulos (2D) de T0: %s graus" % np.array2string(np.degrees(subspace_angles(Nf, N2)), precision=2))
        vf = np.linalg.svd(Jf[:, :4])[2][-1]
        v2 = np.linalg.svd(J2[:, :4])[2][-1]
        log("  direcao quase nula intrinseca: completo %s ; so 22 %s ; angulo %.2f graus"
            % (np.array2string(vf, precision=4), np.array2string(v2, precision=4), np.degrees(np.arccos(min(1, abs(vf @ v2))))))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(linhas) + "\n")
