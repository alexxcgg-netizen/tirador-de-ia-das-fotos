"""Verificacao D2: onde ficam as bandas em M f do exp20 em relacao a janela de hibridizacao do NRHybSur3dq8_CCE
(Yoo et al. 2023, arXiv:2306.03148, secao II: janela ~2500-3500 M antes do pico; antes disso amplitudes PN 3,5PN e
fase SEOBNRv4_opt). Imprime M f_22 em u = -5000, -3500, -2500, -1000 M (u = 0 no pico)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import observaveis as O
for (q, c1, c2) in ((1.0, 0.0, 0.0), (1.2, 0.3, -0.2), (3.0, 0.6, 0.0)):
    t, h, ti = O.gerar_janela(q, c1, c2, 65.0, 6.0)
    w22, _ = O._freq22(t, h[(2, 2)])
    tp = t[np.argmax(np.abs(h[(2, 2)]))]
    out = []
    for u in (-8000, -5000, -3500, -2500, -1000):
        out.append('u=%d: Mf=%.4f' % (u, np.interp(tp + u, t, w22) / (2 * np.pi)))
    # instantes em que M f = 0.002, 0.003, 0.006, 0.014
    mf = w22 / (2 * np.pi)
    k0 = int(np.searchsorted(t, ti))
    us = []
    for f in (0.002, 0.003, 0.006, 0.014):
        i = k0 + int(np.argmax(mf[k0:] >= f))
        us.append('Mf=%.3f em u=%.0f' % (f, t[i] - tp))
    print('q=%.1f chi=(%.1f,%.1f): ' % (q, c1, c2) + '; '.join(out) + ' | ' + '; '.join(us), flush=True)
    del t, h
