"""Revisor R4, tarefa 3 (complemento): frequencia instantanea no inicio da janela das binarias excentricas do exp12.

Com EccIC = 1, o exp12 fixa a frequencia orbital MEDIA (f_onda media = 10 Hz). Para l0 = 0 (periastro) a
frequencia instantanea inicial e maior; para l0 = pi (apoastro), menor. Registra omega_inst/omega_avg e a
faixa da frequencia de onda instantanea do (2,2) na primeira orbita radial (min e max em Hz).
Saida: resultados/revisao/rev_R4_freq_inicial.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402

linhas = []
for nome, q, c1, c2, M, e0 in [("B e0=0.2 qB=2", 2.0, 0.05960457850002948, 0.0, 72.5875185658003, 0.2),
                               ("B e0=0.3 qB=2", 2.0, 0.18331746249982117, 0.0, 73.2318162082271, 0.3),
                               ("B e0=0.3 qB=1.2", 1.2, 0.6706318745992426, -0.2, 67.39032577550046, 0.3)]:
    for l0 in (0.0, np.pi):
        f0 = M * C.Dt.MSUN_S * C.F_FIS
        t, h, mod = C.gerar(q, c1, c2, f0, e0, l0, debug=True)
        Ms = M * C.Dt.MSUN_S
        f22 = -np.gradient(np.unwrap(np.angle(h[(2, 2)])), t) / (2 * np.pi * Ms)
        Tr = 2 * np.pi / mod.omega_avg * 1.2               # pouco mais de um periodo orbital medio
        sel = (t - t[0]) < Tr
        linhas.append("%-16s l0 = %.0f pi: omega_inst/omega_avg = %.3f ; f22 instantanea na 1a orbita: %.1f a %.1f Hz (media pedida 10 Hz)"
                      % (nome, l0 / np.pi, mod.omega_inst / mod.omega_avg, f22[sel][5:].min(), f22[sel][5:].max()))
        del t, h, mod
print("\n".join(linhas))
with open(os.path.join(C.RES, "rev_R4_freq_inicial.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
