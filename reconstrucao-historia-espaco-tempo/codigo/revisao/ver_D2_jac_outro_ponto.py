"""Verificacao D2: o espectro de 2 e 3 janelas (exp21) num ponto diferente do espaco de parametros, com passos
padrao e passos x2 (para conferir a estabilidade de sigma_6). Janelas 10, 19.4, 37.5 Hz (as do exp21 para M=65)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import exp20_comum as C
NOMES = ("q", "c1", "c2", "M", "iota", "D")
fr = [10.0, 10.0 * (37.48 / 10.0) ** 0.5, 37.48]
for par in (dict(q=2.0, c1=0.5, c2=0.0, M=65.0, D=400.0, iota=float(np.radians(50.0)), phi=0.0),
            dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, D=400.0, iota=float(np.radians(50.0)), phi=0.0)):
    for fat in (1.0, 2.0):
        if par["q"] == 1.2 and fat == 1.0:
            continue          # o ponto A com passos padrao ja esta no exp21
        t0 = time.time()
        p = dict(q=2e-3 * fat, c1=2e-3 * fat, c2=2e-3 * fat, M=5e-4 * par["M"] * fat, iota=1e-4, D=1e-3 * par["D"], phi=1e-4)
        J, y0 = C.jacobiano(par, fr, nomes=NOMES, passos=p)
        J = J.reshape(3, 4, 6)
        out = []
        for nome, tip, idx in (("T0 K=2", [0, 1, 2, 3], [0, 2]), ("T0 K=3", [0, 1, 2, 3], [0, 1, 2]),
                               ("O0 K=2", [0, 1], [0, 2]), ("O0 K=3", [0, 1], [0, 1, 2])):
            A = J[idx][:, tip, :].reshape(-1, 6)
            s, _ = C.svd_escalado(A, par, NOMES)
            out.append("%s: %s" % (nome, " ".join("%.2e" % z for z in s)))
        print("q=%.1f chi=(%.1f,%.1f) passos x%.0f (%.0f s):\n   " % (par["q"], par["c1"], par["c2"], fat, time.time() - t0)
              + "\n   ".join(out), flush=True)
