"""Experimento 28 (L12): constante otima da desigualdade memoria-energia |Delta h| <= c_L E_rad / D.

Formula de Thorne 1992 (G = c = 1, h = r (h_+ - i h_x)):
    D Delta h(N) = 4 int F(n') K(n', N) dOmega',   K = (n'.mbar)^2 / (1 - n'.N),  mbar = (e_th - i e_ph)/sqrt2,
com F = dE/dOmega' >= 0. Como |K| = (1 + n'.N)/2 <= 1, |D Delta h| <= 4 E (supremo, atingido no limite de um feixe
apontado para o observador).

Para radiacao gravitacional com multipolos 2 <= l <= L, F = (1/16 pi) sum_jk B_jk Y_j conj(Y_k) (Y = -2Y_lm) e
E = tr B / 16 pi, com B = int hdot hdot^dagger du semidefinida positiva (qualquer B >= 0 e realizavel: soma de
surtos disjuntos). Entao
    D Delta h(N) = sum_jk B_jk Gamma_jk,  Gamma_jk = (1/4 pi) int Y_j conj(Y_k) K dOmega,
e   c_L = sup_B |D Delta h| / E = 16 pi max_alpha lambda_max( (e^{i alpha} X + e^{-i alpha} X^dagger)/2 ),  X = Gamma^T
(autovalor generalizado com a matriz de Gram da energia = identidade, porque os Y_j sao ortonormais).

Partes:
  (a) convencoes: Thorne (nucleo K na grade com N no polo) contra memorias.CalculadoraMemoria (formula de modos de
      Mitman et al. 2020), para B aleatorias, L = 2..5; e num N generico (grade girada; F e escalar).
  (b) c_L para L = 2..8, 10, 12, 16, 20, 24, 32; independencia de alpha; estrutura do autovetor otimo; ajuste
      4 - c_L ~ a / L^p.
  (c) radiacao de um so multipolo l (so modos com l fixo) e so l = 2 com |m| = 2 (tipo binaria no plano).
Saida: resultados/exp28_constantes.txt, resultados/exp28_constantes.json
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harmonicos import Grade, sYlm, modos          # noqa: E402
from memorias import CalculadoraMemoria             # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def nucleo_polo(g):
    """K(n', N = z) com mbar = (x - i y)/sqrt2 (base e_th, e_ph de theta = 0, phi = 0)."""
    return (1 + np.cos(g.theta)) / 2 * np.exp(-2j * g.phi)


def matriz_gamma(lista, g):
    K = nucleo_polo(g)
    Y = np.array([g.Y(-2, l, m).ravel() for (l, m) in lista])
    w = (g.peso * K).ravel()
    return (Y * w) @ Y.conj().T / (4 * np.pi)            # Gamma_jk = (1/4pi) int Y_j conj(Y_k) K


def c_otimo(Gam, alfa=0.0):
    X = Gam.T
    H = 0.5 * (np.exp(1j * alfa) * X + np.exp(-1j * alfa) * X.conj().T)
    ev, V = np.linalg.eigh(H)
    return 16 * np.pi * ev[-1], V[:, -1]


def grade_para(L):
    return Grade(2 * L + 12, 4 * L + 16)


# ------------------------------------------------------------------ (a) convencoes
log("(a) Formula de Thorne (nucleo K, N no polo) contra a formula de modos de memorias.py")
rng = np.random.default_rng(28)
erros = []
for L in (2, 3, 4, 5):
    lista = modos(L, 2)
    n = len(lista)
    calc = CalculadoraMemoria(lista)
    g = grade_para(L)
    Gam = matriz_gamma(lista, g)
    for rep in range(3):
        X = rng.normal(size=(n, 4)) + 1j * rng.normal(size=(n, 4))
        Bm = X @ X.conj().T
        m = calc.memorias_gram(Bm, np.zeros((n, n), complex))
        z_modos = sum(c * complex(sYlm(-2, l, mm, 0.0, 0.0)) for (l, mm), c in m["deslocamento"].items())
        z_thorne = np.sum(Bm * Gam)
        erros.append(abs(z_modos - z_thorne) / abs(z_thorne))
        if rep == 0:
            log("  L=%d: modos %.12f%+.12fi | Thorne %.12f%+.12fi | E = %.10f (tr B/16pi = %.10f)" % (
                L, z_modos.real, z_modos.imag, z_thorne.real, z_thorne.imag, m["energia_total"],
                np.real(np.trace(Bm)) / (16 * np.pi)))
log("  maior diferenca relativa (12 casos): %.2e" % max(erros))

# N generico: grade girada (o polo da grade aponta para N); F e escalar, K usa a base (e_th, e_ph) de N
th0, ph0 = 1.1, 0.7
Nv = np.array([np.sin(th0) * np.cos(ph0), np.sin(th0) * np.sin(ph0), np.cos(th0)])
eth = np.array([np.cos(th0) * np.cos(ph0), np.cos(th0) * np.sin(ph0), -np.sin(th0)])
eph = np.array([-np.sin(ph0), np.cos(ph0), 0.0])
mbar = (eth - 1j * eph) / np.sqrt(2)
gr = Grade(60, 120)
# pontos da grade girada: n' = cos(t) N + sin(t)(cos(p) eth + sin(p) eph)
nx = (np.cos(gr.theta)[..., None] * Nv + np.sin(gr.theta)[..., None]
      * (np.cos(gr.phi)[..., None] * eth + np.sin(gr.phi)[..., None] * eph))
thp = np.arccos(np.clip(nx[..., 2], -1, 1))
php = np.arctan2(nx[..., 1], nx[..., 0])
Kg = (nx @ mbar) ** 2 / (1 - np.cos(gr.theta))
Kg[np.isclose(gr.theta, 0)] = 0.0
L = 4
lista = modos(L, 2)
n = len(lista)
calc = CalculadoraMemoria(lista)
X = rng.normal(size=(n, 4)) + 1j * rng.normal(size=(n, 4))
Bm = X @ X.conj().T
Yp = np.array([sYlm(-2, l, mm, thp, php) for (l, mm) in lista])
F = np.real(np.einsum("jk,jab,kab->ab", Bm, Yp, Yp.conj())) / (16 * np.pi)
z_thorne = 4 * gr.integrar(F * Kg)
m = calc.memorias_gram(Bm, np.zeros((n, n), complex))
z_modos = sum(c * complex(sYlm(-2, l, mm, th0, ph0)) for (l, mm), c in m["deslocamento"].items())
log("  N generico (theta=%.1f, phi=%.1f), L=4: modos %.12f%+.12fi | Thorne %.12f%+.12fi | dif rel %.1e" % (
    th0, ph0, z_modos.real, z_modos.imag, z_thorne.real, z_thorne.imag, abs(z_modos - z_thorne) / abs(z_modos)))
log("  => mesma normalizacao e mesmo sinal: D Delta h = 4 int F K dOmega' com h = r(h_+ - i h_x) do projeto.")

# ------------------------------------------------------------------ (b) constantes otimas
log()
log("(b) c_L = sup |D Delta h(N)| / E_rad sobre radiacao com 2 <= l <= L (fluencias de ondas gravitacionais)")
res = {}
for L in (2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 20, 24, 32):
    lista = modos(L, 2)
    g = grade_para(L)
    Gam = matriz_gamma(lista, g)
    cs = [c_otimo(Gam, a)[0] for a in (0.0, 0.4, 1.3, 2.9)]
    c, v = c_otimo(Gam, 0.0)
    peso_l = {}
    for k, (l, mm) in enumerate(lista):
        peso_l[l] = peso_l.get(l, 0.0) + abs(v[k]) ** 2
    pm = {}
    for k, (l, mm) in enumerate(lista):
        pm[mm] = pm.get(mm, 0.0) + abs(v[k]) ** 2
    # posto do autovetor (o otimo e de posto 1?) e segundo autovalor
    X = Gam.T
    ev = np.linalg.eigvalsh(0.5 * (X + X.conj().T))
    res[L] = dict(c=float(c), c_sobre_4=float(c / 4), var_alfa=float(max(cs) - min(cs)),
                  segundo=float(16 * np.pi * ev[-2]), peso_l={int(k): float(x) for k, x in peso_l.items()},
                  m_dominante=int(max(pm, key=pm.get)), peso_m_dom=float(max(pm.values())))
    log("  L=%2d: c_L = %.10f  (c_L/4 = %.6f; 4 - c_L = %.3e; var. com alpha %.1e; 2o autovalor x16pi = %.6f)" % (
        L, c, c / 4, 4 - c, max(cs) - min(cs), 16 * np.pi * ev[-2]))
    log("        autovetor: m = %d (peso %.6f); pesos por l: %s" % (
        res[L]["m_dominante"], res[L]["peso_m_dom"],
        ", ".join("%d:%.3f" % (k, x) for k, x in sorted(peso_l.items()))))
Ls = np.array([L for L in res if L >= 6], float)
ds = np.array([4 - res[int(L)]["c"] for L in Ls])
p, la = np.polyfit(np.log(Ls), np.log(ds), 1)
log("  ajuste 4 - c_L ~ a L^p (L >= 6): p = %.4f, a = %.4f" % (p, np.exp(la)))
# racionalidade / forma fechada de c_2
c2 = res[2]["c"]
log("  c_2 = %.15f ; c_2 * 3 = %.12f ; c_2 * 5 = %.12f ; c_2*7 = %.12f; c_2^2 = %.12f" % (
    c2, 3 * c2, 5 * c2, 7 * c2, c2 * c2))

# ------------------------------------------------------------------ (b2) L grande, metodo 1D
log()
log("(b2) L grande: Gamma so acopla m_j = m_k + 2 (K ~ e^{-2 i phi}); integral so em theta (Gauss-Legendre),")
log("     harmonicos do pacote `spherical` (mesma convencao de harmonicos.sYlm, conferida), autovalor por eigsh")
import scipy.sparse as sp                              # noqa: E402
from scipy.sparse.linalg import eigsh                  # noqa: E402
import quaternionic                                    # noqa: E402
import spherical                                       # noqa: E402


def c_1d(L):
    x, wq = np.polynomial.legendre.leggauss(L + 12)
    th = np.arccos(x)
    R = quaternionic.array.from_spherical_coordinates(th, np.zeros_like(th))
    W = spherical.Wigner(L)
    Yall = np.real(W.sYlm(-2, R))                      # (n_theta, n_modos), real em phi = 0
    lista = modos(L, 2)
    idx = {lm: k for k, lm in enumerate(lista)}
    cols = np.array([W.Yindex(l, m) for (l, m) in lista])
    Yt = Yall[:, cols]
    peso = wq * (1 + x) / 2 * 0.5                       # (1/4pi) * 2pi * (1+x)/2
    rows, colsI, vals = [], [], []
    for m in range(-L, L - 1):
        J = [idx[(l, m + 2)] for l in range(max(2, abs(m + 2)), L + 1)]
        Kk = [idx[(l, m)] for l in range(max(2, abs(m)), L + 1)]
        if not J or not Kk:
            continue
        G = (Yt[:, J] * peso[:, None]).T @ Yt[:, Kk]    # Gamma_jk, j em m+2, k em m
        for a_, j in enumerate(J):
            for b_, k in enumerate(Kk):
                rows.append(k); colsI.append(j); vals.append(0.5 * G[a_, b_])   # H = (X + X^T)/2, X = Gamma^T
                rows.append(j); colsI.append(k); vals.append(0.5 * G[a_, b_])
    n = len(lista)
    Hs = sp.csr_matrix((vals, (rows, colsI)), shape=(n, n))
    ev = eigsh(Hs, k=2, which="LA", return_eigenvectors=False, tol=1e-12)
    return 16 * np.pi * float(np.max(ev))


res["L_grande"] = {}
for L in (8, 16, 32, 48, 64, 96, 128):
    c = c_1d(L)
    res["L_grande"][L] = c
    ref = (" | 2D: %.10f" % res[L]["c"]) if L in res else ""
    log("  L=%3d: c_L = %.10f  4 - c_L = %.5e  L(4 - c_L) = %.5f%s" % (L, c, 4 - c, L * (4 - c), ref))
Lg = np.array(sorted(res["L_grande"]), float)
dg = np.array([4 - res["L_grande"][int(L)] for L in Lg])
for i in range(1, len(Lg)):
    log("  expoente local entre L=%d e %d: %.4f" % (Lg[i - 1], Lg[i], np.log(dg[i] / dg[i - 1]) / np.log(Lg[i] / Lg[i - 1])))

# ------------------------------------------------------------------ (c) casos restritos
log()
log("(c) Casos restritos")
for l in (2, 3, 4, 6, 8):
    lista = [(l, m) for m in range(-l, l + 1)]
    g = grade_para(l)
    c, v = c_otimo(matriz_gamma(lista, g))
    res.setdefault("so_l", {})[l] = float(c)
    log("  so o multipolo l=%d: c = %.10f" % (l, c))
# binaria quadrupolar no referencial da FONTE: so (2,+-2), B = diag(b, b) (os termos cruzados se anulam na media
# temporal porque h22 e h2-2 tem frequencias opostas); memoria no observador em inclinacao iota
lista = [(2, 2), (2, -2)]
calc = CalculadoraMemoria(lista)
Bq = np.diag([1.0, 1.0]).astype(complex)
mq = calc.memorias_gram(Bq, np.zeros((2, 2), complex))
Eq = mq["energia_total"]
io = np.linspace(0, np.pi, 181)
razao = [abs(sum(c * complex(sYlm(-2, l, mm, i, 0.0)) for (l, mm), c in mq["deslocamento"].items())) / Eq for i in io]
k = int(np.argmax(razao))
res["quadrupolo_fonte"] = dict(max=float(razao[k]), iota_max=float(io[k]), razao_iota90=float(razao[90]))
log("  quadrupolo de binaria (so (2,+-2) no referencial da fonte, B = diag): max_iota |D Dh|/E = %.10f em iota = %.1f graus"
    % (razao[k], np.degrees(io[k])))
log("     = %.6f c_2 = %.6f x 4 ; 17/24 = %.10f" % (razao[k] / res[2]["c"], razao[k] / 4, 17 / 24))
for ideg in (0, 30, 50, 70, 90):
    i = np.radians(ideg)
    z = sum(c * complex(sYlm(-2, l, mm, i, 0.0)) for (l, mm), c in mq["deslocamento"].items())
    z = z / Eq
    log("     iota=%2d: D Dh/E = %+.10f %+.1ei ; D Dh / [E sin^2 iota (17 + cos^2 iota)] = %.10f (1/24 = %.10f)" % (
        ideg, z.real, z.imag, (z.real / (np.sin(i) ** 2 * (17 + np.cos(i) ** 2))) if ideg else float("nan"), 1 / 24))
with open(os.path.join(RES, "exp28_constantes.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(RES, "exp28_constantes.json"), "w") as f:
    json.dump({str(k): v for k, v in res.items()}, f, indent=1)
