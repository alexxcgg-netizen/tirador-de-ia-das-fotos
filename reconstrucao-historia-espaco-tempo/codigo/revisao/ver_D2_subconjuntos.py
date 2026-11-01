"""Verificacao D2: robustez dos valores singulares de K janelas (exp21) a escolha das janelas.
Usa o jacobiano salvo em resultados/exp21_jacobianos_K.npz (49 janelas, T0, passos h e h/2) e examina TODOS os
subconjuntos de K = 2, 3 janelas (O0 e T0), e amostras de K = 4. Sem regerar ondas."""
import itertools, os
import numpy as np
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = np.load(os.path.join(RAIZ, 'resultados', 'exp21_jacobianos_K.npz'))
fr = d['freqs']; nf = len(fr)
esc = np.array([0.1, 0.1, 0.1, 1.0, 0.01, 4.0])   # escalas R4 (D = 400 Mpc -> 0.01 D = 4)
J1 = d['T0_J'].reshape(nf, 4, 6) * esc; J2 = d['T0_J2'].reshape(nf, 4, 6) * esc
def sv(J, idx, tip):
    A = J[list(idx)][:, tip, :].reshape(-1, 6)
    return np.linalg.svd(A, compute_uv=False)
for nome, tip in (('O0', [0, 1]), ('T0', [0, 1, 2, 3])):
    for K in (2, 3):
        res = []
        for idx in itertools.combinations(range(nf), K):
            s1 = sv(J1, idx, tip); s2 = sv(J2, idx, tip)
            if len(s1) < 6: continue
            res.append((s1[5], abs(s2[5] / s1[5] - 1), idx))
        if not res: continue
        a = np.array([r[0] for r in res]); e = np.array([r[1] for r in res])
        i_max = int(np.argmax(a)); i_min = int(np.argmin(a))
        print('%s K=%d: %d subconjuntos; sigma_6: min %.2e (janelas %s Hz, h/h2 %.0e), mediana %.2e, max %.2e (janelas %s Hz, h/h2 %.0e)'
              % (nome, K, len(res), a[i_min], np.round(fr[list(res[i_min][2])], 1), e[i_min], np.median(a), a[i_max],
                 np.round(fr[list(res[i_max][2])], 1), e[i_max]))
        print('      fracao com |sigma6(h)/sigma6(h/2)-1| > 0.1: %.3f ; sigma6 do subconjunto do relatorio (0,24,48)/(0,48): %s'
              % (np.mean(e > 0.1), [('%.3e' % r[0]) for r in res if r[2] in ((0, 24, 48), (0, 48))]))
# O0 K=3: sigma_6 contra a separacao das janelas
print('O0, K=3 com janelas (0, j, 48): sigma_6 em funcao da janela do meio')
for j in (2, 6, 12, 18, 24, 30, 36, 42, 46):
    print('   f_meio = %.1f Hz: sigma_6 = %.2e (h/2: %.2e)' % (fr[j], sv(J1, (0, j, 48), [0, 1])[5], sv(J2, (0, j, 48), [0, 1])[5]))
