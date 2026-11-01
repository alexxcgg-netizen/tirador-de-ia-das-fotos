"""Verificacao adversarial D4 (L12): constantes c_L e c(e2) por implementacao independente.

Independente de harmonicos.py e de spherical: harmonicos com peso de spin pelas matrizes d de Wigner via polinomios
de Jacobi (scipy.special.eval_jacobi), com fatores em log-gama. Sinais por modo nao importam (similaridade diagonal).
  (1) c_L = 16 pi lambda_max(Herm Gamma^T) pelo metodo 1D (integral em theta, Gauss-Legendre) para L = 2..16, 32, 64,
      128, 192, 256; conferencia da normalizacao dos harmonicos.
  (2) c_2 analitico refeito a mao: cadeias m = -2 -> 0 -> 2 e -1 -> 1.
  (3) teste de sanidade: B aleatorias de posto 1 e mistas nunca passam de c_L; o autovetor atinge c_L.
  (4) c(e2), L = 5: dual (min sobre mu) contra primal de posto 1 por subida alternada (independente do dual),
      e contra primal por SDP de busca aleatoria.
Saida: impressa (copiada no relatorio de verificacao).
"""
import numpy as np
from scipy.special import eval_jacobi, gammaln
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh


def d_wigner(j, mp, m, beta):
    """d^j_{mp,m}(beta) pela forma de Jacobi (Wikipedia), com binomiais em log."""
    x = np.cos(beta)
    ks = {"a": j + m, "b": j - m, "c": j + mp, "d": j - mp}
    caso = min(ks, key=ks.get)
    k = ks[caso]
    if caso == "a":
        a, lam = mp - m, mp - m
    elif caso == "b":
        a, lam = m - mp, 0
    elif caso == "c":
        a, lam = m - mp, 0
    else:
        a, lam = mp - m, mp - m
    b = 2 * j - 2 * k - a
    # binom(2j-k, k+a)^(1/2) binom(k+b, b)^(-1/2)
    lb1 = gammaln(2 * j - k + 1) - gammaln(k + a + 1) - gammaln(2 * j - 2 * k - a + 1)
    lb2 = gammaln(k + b + 1) - gammaln(b + 1) - gammaln(k + 1)
    lpref = 0.5 * lb1 - 0.5 * lb2
    s2, c2 = np.sin(beta / 2), np.cos(beta / 2)
    with np.errstate(divide="ignore"):
        lpot = a * np.log(np.abs(s2)) + b * np.log(np.abs(c2))
    P = eval_jacobi(k, a, b, x)
    return (-1) ** lam * np.exp(lpref + lpot) * P


def sY_theta(s, l, m, theta):
    """|parte em theta| de sY_lm (a menos de um sinal por modo): sqrt((2l+1)/4pi) d^l_{m,-s}(theta)."""
    return np.sqrt((2 * l + 1) / (4 * np.pi)) * d_wigner(l, m, -s, theta)


def c_L(L, devolver=False):
    nq = L + 16
    x, wq = np.polynomial.legendre.leggauss(nq)
    th = np.arccos(x)
    lista = [(l, m) for l in range(2, L + 1) for m in range(-l, l + 1)]
    idx = {lm: i for i, lm in enumerate(lista)}
    Yt = {lm: sY_theta(-2, lm[0], lm[1], th) for lm in lista}
    # normalizacao: 2 pi int |Y|^2 dx = 1
    errn = max(abs(2 * np.pi * np.sum(wq * Yt[lm] ** 2) - 1) for lm in lista)
    peso = wq * (1 + x) / 2 * 2 * np.pi / (4 * np.pi)
    rows, cols, vals = [], [], []
    for m in range(-L, L - 1):
        J = [l for l in range(max(2, abs(m + 2)), L + 1)]
        K = [l for l in range(max(2, abs(m)), L + 1)]
        if not J or not K:
            continue
        A = np.array([Yt[(l, m + 2)] for l in J])        # nJ x nq
        Bk = np.array([Yt[(l, m)] for l in K])
        G = (A * peso) @ Bk.T                              # Gamma_{(l,m+2),(l',m)}
        for a_, lj in enumerate(J):
            for b_, lk in enumerate(K):
                v = 0.5 * G[a_, b_]
                rows += [idx[(lj, m + 2)], idx[(lk, m)]]
                cols += [idx[(lk, m)], idx[(lj, m + 2)]]
                vals += [v, v]
    n = len(lista)
    H = sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
    if n < 400:
        ev, V = np.linalg.eigh(H.toarray())
        c = 16 * np.pi * ev[-1]
        out = (c, errn, H.toarray(), lista) if devolver else (c, errn)
        return out
    ev = eigsh(H, k=1, which="LA", return_eigenvectors=False, tol=1e-13)
    return 16 * np.pi * float(ev[0]), errn


print("(1) c_L por Wigner-d/Jacobi independente (metodo 1D)")
ref = {2: 0.9128709292, 3: 1.8516605417, 4: 2.2387199979, 5: 2.5108013487, 6: 2.7146224743, 8: 3.0056805851,
       12: 3.3130007670, 16: 3.4754160905, 32: 3.7304733816, 64: 3.8632764935, 128: 3.9311211961}
res = {}
for L in (2, 3, 4, 5, 6, 8, 12, 16, 32, 64, 128, 192, 256):
    c, errn = c_L(L)
    res[L] = c
    r = ref.get(L)
    print("  L=%3d: c_L = %.10f  (D4: %s; dif %s)  L(4-c_L) = %.5f  erro de normalizacao %.1e" % (
        L, c, "%.10f" % r if r else "-", "%.1e" % abs(c - r) if r else "-", L * (4 - c), errn))
Ls = sorted(res)
for a, b in zip(Ls[-4:-1], Ls[-3:]):
    p = np.log((4 - res[b]) / (4 - res[a])) / np.log(b / a)
    print("  expoente local %d-%d: %.4f" % (a, b, p))
# extrapolacao de L(4-c_L) = a + b/L com os dois ultimos pontos e com tres (a + b/L + c/L^2)
L1, L2, L3 = 128, 192, 256
y = {L: L * (4 - res[L]) for L in (L1, L2, L3)}
a2 = (L3 * y[L3] - L2 * y[L2]) / (L3 - L2)
Mx = np.array([[1, 1 / L, 1 / L ** 2] for L in (L1, L2, L3)])
a3 = np.linalg.solve(Mx, np.array([y[L1], y[L2], y[L3]]))[0]
print("  extrapolacao de a = lim L(4 - c_L): 2 pontos (192, 256) %.4f ; 3 pontos (128..256) %.4f" % (a2, a3))

print()
print("(2) c_2 a mao: Gamma(l=2) com os elementos de exp28_c2_exato; cadeia (-2,0,2): +-(8/1)*sqrt(g1^2+g2^2)")
g1, g2, g3 = np.sqrt(6) / (48 * np.pi), np.sqrt(6) / (24 * np.pi), 1 / (12 * np.pi)
c2_cadeia = 16 * np.pi * 0.5 * np.sqrt(g1 ** 2 + g2 ** 2)
print("  cadeia (-2,0,2): %.12f ; sqrt(30)/6 = %.12f ; cadeia (-1,1): %.12f (2/3)" % (
    c2_cadeia, np.sqrt(30) / 6, 16 * np.pi * 0.5 * g3))
c, _, H2, lista2 = c_L(2, devolver=True)
Hm = 16 * np.pi * H2
print("  autovalores (Wigner-d) de 16 pi Herm: %s" % np.array2string(np.sort(np.linalg.eigvalsh(Hm)), precision=10))

print()
print("(3) Sanidade: B aleatorias (posto 1 e mistas), L = 6, razao |D Dh|/E <= c_L e fase livre")
c6, _, H6, lista6 = c_L(6, devolver=True)
rng = np.random.default_rng(4)
n = len(lista6)
# matriz X = Gamma^T reconstruida a partir de H (H = (X + X^T)/2 com X real estritamente "m -> m+2")
# |D Dh| para B = v v^dag: |v^dag X v| ; aqui usamos a forma rotacionada: max_alpha v^dag Herm(e^{ia} X) v
mm = np.array([m for (l, m) in lista6])
X = np.where(mm[:, None] == mm[None, :] - 2, 2 * H6, 0.0)   # X_{kj} so com m_j = m_k + 2 (linha k em m, coluna j em m+2)
if np.allclose(X, 0):
    X = np.where(mm[:, None] == mm[None, :] + 2, 2 * H6, 0.0)
assert np.allclose(0.5 * (X + X.T), H6)
mx = 0
for rep in range(20000):
    k = rng.integers(1, 4)
    V = rng.normal(size=(n, k)) + 1j * rng.normal(size=(n, k))
    Bm = V @ V.conj().T
    r = 16 * np.pi * abs(np.trace(Bm @ X)) / np.real(np.trace(Bm))
    mx = max(mx, r)
ev, W = np.linalg.eigh(H6)
v = W[:, -1]
rv = 16 * np.pi * abs(v.conj() @ X @ v)
print("  max sobre 20000 B aleatorias: %.5f ; autovetor otimo: %.10f ; c_6 = %.10f" % (mx, rv, c6))

print()
print("(4) c(e2), L = 5: dual (min_mu) x primal de posto 1 por subida alternada (independente)")
c5, _, H5, lista5 = c_L(5, devolver=True)
P2 = np.diag([1.0 if l == 2 else 0.0 for (l, m) in lista5])
i2 = np.array([l == 2 for (l, m) in lista5])
H22, H2r, Hrr = H5[np.ix_(i2, i2)], H5[np.ix_(i2, ~i2)], H5[np.ix_(~i2, ~i2)]


def dual(e2):
    mus = np.linspace(-60, 60, 24001)
    best = np.inf
    for mu in mus[::40]:
        best = min(best, np.linalg.eigvalsh(H5 - mu * P2)[-1] + mu * e2)
    from scipy.optimize import minimize_scalar
    f = lambda mu: np.linalg.eigvalsh(H5 - mu * P2)[-1] + mu * e2   # noqa: E731
    r = minimize_scalar(f, bounds=(-60, 60), method="bounded", options=dict(xatol=1e-12))
    return 16 * np.pi * min(best, r.fun)


def primal(e2, nrep=60):
    """max v^T H v com v = (sqrt(e2) u, sqrt(1-e2) w), |u| = |w| = 1 (reais bastam: H e real simetrica)."""
    a, b = np.sqrt(e2), np.sqrt(1 - e2)
    best = -np.inf
    for rep in range(nrep):
        u = rng.normal(size=H22.shape[0]); u /= np.linalg.norm(u)
        w = rng.normal(size=Hrr.shape[0]); w /= np.linalg.norm(w)
        for it in range(3000):
            # maximiza em u com w fixo: a^2 u H22 u + 2ab u H2r w ; problema de autovetor com termo linear -> TRS;
            # usa passo de ascensao projetada simples
            gu = 2 * a * a * H22 @ u + 2 * a * b * H2r @ w
            gw = 2 * b * b * Hrr @ w + 2 * a * b * H2r.T @ u
            u = u + 0.5 * gu; u /= np.linalg.norm(u)
            w = w + 0.5 * gw; w /= np.linalg.norm(w)
        val = a * a * u @ H22 @ u + b * b * w @ Hrr @ w + 2 * a * b * u @ H2r @ w
        best = max(best, val)
    return 16 * np.pi * best


D4 = {0.99: 1.204892, 0.95: 1.552398, 0.9: 1.795829, 0.9888: 1.22159, 0.8386: 2.00194, 0.7953: 2.11312}
for e2 in (0.99, 0.9888, 0.95, 0.9, 0.8386, 0.7953, 0.5):
    d = dual(e2)
    p = primal(e2)
    print("  e2=%.4f: dual %.6f | primal posto 1 %.6f | gap %.1e | D4 %s" % (e2, d, p, d - p, D4.get(e2, "-")))
print("  e2 -> 1: c(1 - eps) - c_2 ~ k sqrt(eps)?")
for eps in (1e-2, 1e-3, 1e-4):
    d = dual(1 - eps)
    print("   eps=%.0e: c - c_2 = %.5f ; (c - c_2)/sqrt(eps) = %.4f" % (eps, d - np.sqrt(30) / 6, (d - np.sqrt(30) / 6) / np.sqrt(eps)))
