"""Verificacao adversarial D1 (H1.3): o posto 4 de T no polo (iota = 0) depende da coluna phi'?

No polo as coordenadas (iota, phi') sao singulares: rodar phi' em iota = 0 nao move o observador, so gira a base de
polarizacao (-2Y_l2(0, phi) ~ exp(2 i phi)). Logo a coluna phi' no polo e uma rotacao da base de polarizacao, que um
detector com psi desconhecido nao separa. Teste: SVD de T no polo com e sem a coluna phi' (e sem iota), com os dados
do proprio exp17 (resultados/exp17_jac_A.npz, funcao jacobiano de exp17_analise_jac), escala abs; e perto do polo.
Saida: resultados/ver_D1_polo.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import exp17_analise_jac as J                       # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "ver_D1_polo.txt")

if __name__ == "__main__":
    L = []
    dp = J.carregar_A()
    j = 1                                          # M = 65 (lista do ponto A: MS = 30, 65, 120)
    Fr = J.fref(dp, j)
    s = 1 / np.abs(Fr)
    COLS = J.COLS
    for io_g in (0.0, 1.0, 5.0, 50.0):
        for phi in (0.0, 1.0):
            for m0, nome in ((False, "T"), (True, "T0")):
                F0, Jm, E = J.jacobiano(dp, j, np.radians(io_g), phi, m0)
                Js, Es = Jm * s[:, None], E * s[:, None]
                for rot, cols in (("todas", [0, 1, 2, 3, 4, 5, 6]), ("sem phi'", [0, 1, 2, 3, 4, 5]),
                                  ("sem phi', iota", [0, 1, 2, 3, 4]), ("intr", [0, 1, 2, 3])):
                    if m0 and 6 in cols:
                        continue
                    sv = np.linalg.svd(Js[:, cols], compute_uv=False)
                    tau = np.linalg.norm(Es[:, cols])
                    L.append("iota %4.1f phi' %.1f %-2s %-15s sigma = %s ; tau = %.1e ; posto %d"
                             % (io_g, phi, nome, rot, np.array2string(sv, precision=4), tau, int(np.sum(sv > tau))))
        L.append("")
    print("\n".join(L))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(L) + "\n")
