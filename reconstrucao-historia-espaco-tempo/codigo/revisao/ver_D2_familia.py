"""Verificacao D2: re-resolve a familia do exp22 com outro otimizador (scipy least_squares, metodo 'lm' sem limites,
x_scale proprio) para O0 K=3 e T0 K=2 (10 e 37,5 Hz) em q_B = 1.6, partindo de A (q trocado) e de uma partida
deslocada. Residuo relativo r = (y_B - y_A)/|y_A| como no exp22."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from scipy.optimize import least_squares
import exp20_comum as C
from deteccao import MSUN_S
A = C.PAR_A
FMAX = 0.012 / (A["M"] * MSUN_S)
casos = {"O0_K3": (("deslocamento", "spin"), C.freqs_geom(10.0, FMAX, 3)),
         "T0_K2": (C.TIPOS, C.freqs_geom(10.0, FMAX, 2))}
for nome, (tipos, fr) in casos.items():
    yA = C.observaveis_K(A, fr, tipos=tipos).ravel()
    def res(z, qB):
        p = dict(q=qB, c1=z[0], c2=z[1], M=z[2], iota=np.radians(z[3]), D=z[4], phi=0.0)
        return (C.observaveis_K(p, fr, tipos=tipos).ravel() - yA) / np.abs(yA)
    for qB in (1.6,):
        for rot, z0 in (("partida A", [0.3, -0.2, 65.0, 50.0, 400.0]), ("partida deslocada", [0.1, 0.1, 70.0, 45.0, 380.0])):
            t0 = time.time()
            sol = least_squares(res, z0, args=(qB,), method="lm", x_scale=[0.05, 0.05, 1.0, 1.0, 10.0],
                                diff_step=[3e-3, 3e-3, 2e-5, 2e-5, 2e-5], max_nfev=400, xtol=1e-12, ftol=1e-14)
            r = sol.fun
            print("%s q_B=%.1f %s: max|r| %.2e norma %.2e (%d aval., %.0f s) -> chi1 %+.4f chi2 %+.4f M %.3f iota %.2f D %.1f"
                  % (nome, qB, rot, np.max(np.abs(r)), np.linalg.norm(r), sol.nfev, time.time() - t0, *sol.x), flush=True)
