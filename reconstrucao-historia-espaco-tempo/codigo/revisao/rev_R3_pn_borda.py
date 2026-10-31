"""Revisor R3: o erro de primeira ordem em dt de pn_excentrico vem das pontas (soma ate a separatriz x corte em T - 5 M).

Saida: resultados/revisao/rev_R3_pn_borda.txt
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rev_R3_comum import B, CalculadoraMemoria, CODIGO, gram, SAIDA
linhas = []
sys.path.insert(0, CODIGO)
import pn_excentrico as PE, deteccao as Dt
L = [(2, 2), (2, -2), (2, 0)]
eta = 1.2/2.2**2; f0 = 65*Dt.MSUN_S*10
c = CalculadoraMemoria(L)
for e0 in (0.0, 0.3):
    res = {}
    for dt in (0.5, 0.25, 0.125):
        t, h, r, a, e = PE.modos(eta, e0, f0, dt=dt)
        dt_ = t[1]-t[0]
        H = np.stack([h[k] for k in L], axis=1); Hd = B.derivada4(H, dt_)
        T = t[-1]
        out = []
        for corte in (0.0, 5.0):
            k = int(np.round((T - corte) / dt_))  # corte num tempo fixo antes da separatriz
            sel = slice(0, k + 1) if corte > 0 else slice(None)
            m = c.memorias_gram(*gram(H[sel], Hd[sel], dt_))
            out.append((m["deslocamento"][(2,0)].real, m["spin"][(3,0)].imag, t[sel][-1]))
        res[dt] = out
    for j, nm in enumerate(("ate a separatriz", "ate separatriz - 5 M (pontas fora)")):
        a5, a25, a125 = (res[d][j] for d in (0.5, 0.25, 0.125))
        linhas.append("e0=%.1f %-36s desl20: %+.1e %+.1e  spin30: %+.1e %+.1e  (t_fim: %.3f %.3f %.3f)" % (e0, nm,
              (a25[0]-a5[0])/a125[0], (a125[0]-a25[0])/a125[0], (a25[1]-a5[1])/a125[1], (a125[1]-a25[1])/a125[1], a5[2], a25[2], a125[2]))
print("\n".join(linhas))
open(os.path.join(SAIDA, "rev_R3_pn_borda.txt"), "w").write("\n".join(linhas) + "\n")
