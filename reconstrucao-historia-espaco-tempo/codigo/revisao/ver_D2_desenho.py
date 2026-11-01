"""Verificacao D2: recalculo independente do criterio D (exp23) para A a partir de resultados/exp23_prep_A.npz,
com codigo proprio (sem somas acumuladas), e testes: (i) D(K=2) em funcao do corte; (ii) priors x2 e /2;
(iii) so deslocamento (sem spin); (iv) ganho em sigma_lnM."""
import os
import numpy as np
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPRI = np.array([2.0, 0.5, 0.5, 0.3, 0.5, 0.5])
for nome in ('A', 'M150'):
    d = np.load(os.path.join(RAIZ, 'resultados', 'exp23_prep_%s.npz' % nome))
    par = d['par']; M, D = par[3], par[5]
    V = d['Vb']; dV = d['dVb'].copy(); dV[:, :, 3] *= M; dV[:, :, 5] *= D
    G = {'d': d['Gd_CE'], 's': d['Gs_CE']}
    n = len(V); mf = d['bordas_mf']
    def fisher(cortes, modelo, tipos=(0, 1), spri=SPRI):
        b = [0] + list(cortes) + [n]
        F = np.zeros((6, 6))
        for t, k in ((0, 'd'), (1, 's')):
            if t not in tipos: continue
            Vb = np.array([V[b[i]:b[i+1], t].sum() for i in range(len(b)-1)])
            dVb = np.array([dV[b[i]:b[i+1], t, :].sum(0) for i in range(len(b)-1)])
            Gb = np.array([[G[k][b[i]:b[i+1], b[j]:b[j+1]].sum() for j in range(len(b)-1)] for i in range(len(b)-1)])
            g = dVb / Vb[:, None]
            F += (g.T * np.diag(Gb)) @ g if modelo == 'diag' else g.T @ Gb @ g
        return spri[:, None] * F * spri[None, :]
    def Dcrit(F):
        lam = np.clip(np.linalg.eigvalsh(0.5*(F+F.T)), 0, None); return np.sum(np.log1p(lam))
    def post(F):
        return np.sqrt(np.diag(np.linalg.inv(np.eye(6) + F)))
    print('fonte %s: %d bandas elementares, ultima borda Mf = %.4f' % (nome, n, mf[-1]))
    for modelo in ('diag', 'corr'):
        D1 = Dcrit(fisher([], modelo))
        Ds = [(Dcrit(fisher([c], modelo)), c) for c in range(1, n)]
        best = max(Ds)
        print('  %s: D(K=1) = %.3f ; D(K=2) otimo = %.3f no corte %d/%d (Mf %.4f) ; D no penultimo corte = %.3f ; mediana sobre cortes = %.3f'
              % (modelo, D1, best[0], best[1], n - 1, mf[best[1]], Ds[-2][0], np.median([z[0] for z in Ds])))
        print('      sigma_post/prior K=1:', np.round(post(fisher([], modelo)), 2), ' K=2 otimo:', np.round(post(fisher([best[1]], modelo)), 2))
        for fat in (0.5, 2.0):
            sp_ = SPRI * fat
            D1f = Dcrit(fisher([], modelo, spri=sp_)); D2f = max(Dcrit(fisher([c], modelo, spri=sp_)) for c in range(1, n))
            print('      priors x%.1f: D(K=1) %.3f, D(K=2) %.3f, ganho %.3f' % (fat, D1f, D2f, D2f - D1f))
        D1d = Dcrit(fisher([], modelo, tipos=(0,))); D2d = max((Dcrit(fisher([c], modelo, tipos=(0,))), c) for c in range(1, n))
        print('      so deslocamento: D(K=1) %.3f, D(K=2) %.3f (corte Mf %.4f), sigma_lnM/prior %.2f -> %.2f'
              % (D1d, D2d[0], mf[D2d[1]], post(fisher([], modelo, tipos=(0,)))[3], post(fisher([D2d[1]], modelo, tipos=(0,)))[3]))
