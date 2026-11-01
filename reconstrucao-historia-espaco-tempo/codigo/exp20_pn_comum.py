"""Biblioteca PN das linhas L03/L04 (agente D2): memorias de banda a partir de E(x) e da distribuicao angular dos fluxos.

Fatos usados (derivados no relatorio linhas/L03_L04_janelas.md, secao 2):
  * todas as memorias nulas sao formas bilineares nos modos (h, hdot); numa orbita circular adiabatica
    hdot_lm = -i m Omega h_lm (mais termos de reacao de radiacao, relativos O(x^{5/2})), entao a taxa de cada memoria
    dividida pelo fluxo de energia (deslocamento) ou de momento angular (spin, giroscopica) so depende das AMPLITUDES
    relativas H_lm(x): alpha_L(x) = (dh_L0/du)/(dE/du), beta_L(x) = (dS_L0/du)/(dJ/du).
  * com janelas definidas por frequencia, dm/dx = alpha(x) dE_rad/dx = alpha(x) E_lig'(x) e, pela primeira lei para
    orbitas circulares (dE = Omega dJ, Omega = x^{3/2}/M), dS/dx = beta(x) x^{-3/2} E_lig'(x). O fluxo F(x) (com as
    caudas 4 pi x^{3/2} etc.) CANCELA; so a absorcao no horizonte sobra (fator F_inf/(F_inf + F_H)).

Fontes das expressoes (resultados/exp20_pn_expressoes.json, extraidas por exp20_pn_extrair.py):
  E(x), F(x), F_H, xdot, dU20/dt, H20, H40, H60, H80: Cunningham et al., CQG 42, 135009 (2025), material suplementar
  (spins alinhados ate 3.5PN; s = (m1^2 chi1 + m2^2 chi2)/M^2, sigma = (m2 chi2 - m1 chi1)/M, delta = (m1 - m2)/M);
  h_lm (l <= 4) ate 1.5PN com spin-orbita: Arun, Buonanno, Faye, Ochsner, PRD 79, 104023 (2009), ABFO09.m, no limite
  nao precessante (iota = 0, alpha = pi). Na convencao ABFO, H_lm = i^m H_lm(Blanchet) (fase comum por m).
"""
import functools
import json
import os

import numpy as np
import sympy as sp

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQ = os.path.join(RAIZ, "resultados", "exp20_pn_expressoes.json")

nu, delta, s, sigma, M, DL = sp.symbols("nu delta s sigma M DL", real=True)
x, v = sp.symbols("x v", positive=True)
chis, chia = sp.symbols("chisz chiaz", real=True)
EG = sp.EulerGamma
LOC = dict(nu=nu, delta=delta, s=s, sigma=sigma, x=x, v=v, M=M, DL=DL, chisz=chis, chiaz=chia, pi=sp.pi,
           EulerGamma=EG)


@functools.lru_cache(maxsize=None)
def _expr():
    return json.load(open(ARQ))


def expr(nome):
    return sp.sympify(_expr()[nome], locals=LOC)


def spins_s_sigma(q, chi1, chi2):
    """(nu, delta, s, sigma) de Cunningham et al. (M = 1, m1 >= m2)."""
    m1, m2 = q / (1 + q), 1 / (1 + q)
    return m1 * m2, m1 - m2, m1 ** 2 * chi1 + m2 ** 2 * chi2, m2 * chi2 - m1 * chi1


def subs_num(q, chi1, chi2):
    n, d, ss, sg = spins_s_sigma(q, chi1, chi2)
    return {nu: n, delta: d, s: ss, sigma: sg, chis: 0.5 * (chi1 + chi2), chia: 0.5 * (chi1 - chi2)}


# ------------------------------------------------------------------ truncamento por ordem PN
def serie_em_v(e_chaves, nmax):
    """Expande e_chaves (funcao de x, com x^{k/2} e log x) em v = sqrt(x) e corta v^k, k > nmax (log como O(1))."""
    L = sp.Symbol("L")
    ee = sp.expand(e_chaves.subs(sp.log(16 * x), L + sp.log(16)).subs(sp.log(x), L).subs(x, v ** 2))
    ee = sp.expand(ee)
    p = sp.Poly(ee, v)
    out = 0
    for (k,), c in p.terms():
        if k <= nmax:
            out += c * v ** k
    return out.subs(L, sp.log(v ** 2))


def chaves(nome):
    """Separa H_l0 = prefator(x) * {1 + ...}: devolve (prefator, serie das chaves em x)."""
    e = sp.expand(expr(nome))
    ev = sp.expand(e.subs(x, v ** 2))
    p = sp.Poly(ev, v)
    kmin = min(k for (k,), c in p.terms())
    lead = sp.simplify(p.coeff_monomial(v ** kmin)) * v ** kmin
    serie = sp.expand(sp.simplify(ev / lead))
    return lead.subs(v, sp.sqrt(x)), serie.subs(v, sp.sqrt(x))


# ------------------------------------------------------------------ modos ABFO (amplitudes relativas)
MODOS_ABFO = [(l, m) for l in (2, 3, 4) for m in range(1, l + 1)]


@functools.lru_cache(maxsize=None)
def amplitudes():
    """H_lm(v) normalizados (h_lm = 8 sqrt(pi/5) M nu v^2 / DL * H_lm), m > 0, convencao ABFO; m < 0 por simetria."""
    N = 8 * sp.sqrt(sp.pi / 5) * M * nu * v ** 2 / DL
    out = {}
    for (l, m) in MODOS_ABFO:
        out[(l, m)] = sp.expand(sp.simplify(expr("h%d%d" % (l, m)) / N))
    return out


def amplitudes_completas(ordem_v=3):
    """Dict (l, m) -> H_lm(v) com m = +-1..+-l, cortado em v^ordem_v relativo a v^0 (o H_lm ja inclui as potencias de v)."""
    A = amplitudes()
    out = {}
    for (l, m), e in A.items():
        e2 = sp.expand(e)
        p = sp.Poly(e2, v)
        e3 = sum(c * v ** k for (k,), c in p.terms() if k <= ordem_v)
        out[(l, m)] = e3
        out[(l, -m)] = (-1) ** l * sp.conjugate(e3)
    return out


# ------------------------------------------------------------------ Gaunt exato (deslocamento)
@functools.lru_cache(maxsize=None)
def gaunt(la, lb, m, L):
    """int (-2)Y_{la m} conj((-2)Y_{lb m}) Y_{L0} dOmega (formula dos 3j; conferida em exp20_pn por quadratura)."""
    from sympy.physics.wigner import wigner_3j
    return sp.simplify((-1) ** m * sp.sqrt(sp.Integer((2 * la + 1) * (2 * lb + 1) * (2 * L + 1)) / (4 * sp.pi))
                       * wigner_3j(la, lb, L, m, -m, 0) * wigner_3j(la, lb, L, 2, -2, 0))


def alpha_desl(L, modos, ordem_v=3):
    """alpha_L(v) = (dh^mem_L0/du)/(dE/du) = 16 pi sqrt((L-2)!/(L+2)!) sum m^2 H_a conj(H_b) G / sum m^2 |H_a|^2.

    Expansao em v ate v^ordem_v (relativa). modos: lista (l, m), m > 0 (os m < 0 entram por simetria).
    """
    Hs = amplitudes_completas(ordem_v + 2)
    use = [(l, m) for (l, m) in Hs if (l, abs(m)) in modos]
    num = 0
    den = 0
    for a in use:
        den += a[1] ** 2 * Hs[a] * sp.conjugate(Hs[a])
        for b in use:
            if b[1] != a[1]:
                continue
            G = gaunt(a[0], b[0], a[1], L)
            if G != 0:
                num += a[1] * b[1] * Hs[a] * sp.conjugate(Hs[b]) * G
    c = 16 * sp.pi * sp.sqrt(sp.factorial(L - 2) / sp.factorial(L + 2))
    r = c * num / den
    r = sp.series(sp.expand(r.subs(nu, (1 - delta ** 2) / 4)), v, 0, ordem_v + 1).removeO()
    return sp.expand(sp.simplify(r))


# ------------------------------------------------------------------ nucleos numericos (spin, CM, giroscopica)
@functools.lru_cache(maxsize=None)
def nucleos(modos_tuple, lmax_saida=9):
    """Respostas real-lineares da CalculadoraMemoria a matrizes de Gram elementares, para as saidas m = 0.

    Devolve (lista_modos, K) com K[saida] = (KB_re, KB_im, KA_re, KA_im), arrays (n, n): a saida e
    sum_ab Re(B_ab) KB_re + Im(B_ab) KB_im + Re(A_ab) KA_re + Im(A_ab) KA_im.
    """
    from memorias import CalculadoraMemoria
    lista = []
    for (l, m) in modos_tuple:
        lista += [(l, m), (l, -m)]
    calc = CalculadoraMemoria(lista, lmax_saida)
    n = len(lista)
    saidas = [("deslocamento", (2, 0)), ("deslocamento", (4, 0)), ("spin", (3, 0)), ("spin", (5, 0)),
              ("cm", (2, 0)), ("cm", (4, 0)), ("giroscopica", (1, 0)), ("giroscopica", (3, 0))]
    K = {k: [np.zeros((n, n)) for _ in range(4)] for k in saidas}
    Z = np.zeros((n, n), dtype=complex)

    def val(m, tipo, lm):
        z = m[tipo][lm]
        return float(np.imag(z)) if tipo == "spin" else float(np.real(z))

    for i in range(n):
        for j in range(n):
            if lista[i][1] != lista[j][1]:
                continue
            for qq, (Bm, Am) in enumerate(((1, 0), (1j, 0), (0, 1), (0, 1j))):
                Bx, Ax = Z.copy(), Z.copy()
                Bx[i, j] = Bm
                Ax[i, j] = Am
                m = calc.memorias_gram(Bx, Ax)
                for k in saidas:
                    K[k][qq][i, j] = val(m, *k)
    return lista, K


def taxa_numerica(saida, H, Omega, modos_tuple):
    """Taxa da memoria 'saida' (tipo, (l, 0)) para amplitudes complexas H (dict (l, m) -> valor, m != 0)."""
    lista, K = nucleos(modos_tuple)
    h = np.array([H[k] for k in lista])
    mm = np.array([k[1] for k in lista], dtype=float)
    hd = -1j * mm * Omega * h
    Bm = np.outer(hd, hd.conj())
    Am = np.outer(h, hd.conj())
    KB_re, KB_im, KA_re, KA_im = K[saida]
    return float(np.sum(Bm.real * KB_re + Bm.imag * KB_im + Am.real * KA_re + Am.imag * KA_im))


def amplitudes_numericas(q, chi1, chi2, xx, ordem_v=3, modos=None):
    """Amplitudes H_lm numericas (dict, m = +-) cortadas em v^ordem_v."""
    Hs = amplitudes_completas(ordem_v)
    sub = subs_num(q, chi1, chi2)
    vv = np.sqrt(xx)
    out = {}
    for (l, m), e in Hs.items():
        if modos is not None and (l, abs(m)) not in modos:
            continue
        f = sp.lambdify(v, e.subs(sub), "numpy")
        out[(l, m)] = complex(f(vv))
    return out


def razoes_numericas(q, chi1, chi2, xx, ordem_v=3, modos=None):
    """alpha (deslocamento l=2,4), beta (spin l=3), e as razoes de CM e giroscopica, pela calculadora."""
    modos = tuple(modos or MODOS_ABFO)
    H = amplitudes_numericas(q, chi1, chi2, xx, ordem_v, modos)
    Om = xx ** 1.5
    Edot = sum((m * Om) ** 2 * abs(z) ** 2 for (l, m), z in H.items()) / (16 * np.pi)
    Jdot = Edot / Om
    out = {}
    for saida in [("deslocamento", (2, 0)), ("deslocamento", (4, 0)), ("cm", (2, 0)), ("cm", (4, 0))]:
        out[saida] = taxa_numerica(saida, H, Om, modos) / Edot
    for saida in [("spin", (3, 0)), ("spin", (5, 0)), ("giroscopica", (1, 0)), ("giroscopica", (3, 0))]:
        out[saida] = taxa_numerica(saida, H, Om, modos) / Jdot
    return out


# ------------------------------------------------------------------ energia e momento angular
def E_lig_pos(ordem_v=7):
    """Energia de ligacao positiva E_b(x) = -E(x) (M = 1), chaves cortadas em x^{ordem_v/2}."""
    e = sp.expand(-expr("E").subs(M, 1))
    ch = sp.expand(e / (nu * x / 2))
    return nu * x / 2 * serie_em_v(ch, ordem_v).subs(v, sp.sqrt(x))


def J_primeira_lei(ordem_v=7):
    """J(x) pela primeira lei dJ/dx = -x^{-3/2} dE_b/dx, com a constante fixada pelo termo newtoniano (M = 1)."""
    Eb = E_lig_pos(ordem_v)
    integrando = sp.expand(-sp.diff(Eb, x) * x ** sp.Rational(-3, 2))
    J = sp.integrate(integrando, x)
    return sp.expand(J)


def razao_serie(saida, modos, ordem_v=3, por="J", racionalizar=True):
    """Serie em v da razao (taxa da memoria 'saida')/(fluxo de J ou de E), com os nucleos numericos da calculadora.

    Usa as amplitudes simbolicas (ABFO) e os nucleos K (floats); os coeficientes sao racionalizados com tolerancia
    1e-9 quando racionalizar=True (conferir contra os floats). por='J' (spin, giroscopica) ou 'E' (deslocamento, CM).
    """
    modos = tuple(modos)
    lista, K = nucleos(modos)
    Hs = amplitudes_completas(ordem_v + 2)
    Om = sp.Symbol("Om", positive=True)
    h = [Hs[k] for k in lista]
    mm = [k[1] for k in lista]
    KB_re, KB_im, KA_re, KA_im = K[saida]
    num = 0
    n = len(lista)
    for i in range(n):
        for j in range(n):
            if mm[i] != mm[j]:
                continue
            if max(abs(KB_re[i, j]), abs(KB_im[i, j]), abs(KA_re[i, j]), abs(KA_im[i, j])) < 1e-14:
                continue
            P = h[i] * sp.conjugate(h[j])
            Bij = mm[i] * mm[j] * Om ** 2 * P
            Aij = sp.I * mm[j] * Om * P
            num += (sp.re(Bij) * KB_re[i, j] + sp.im(Bij) * KB_im[i, j]
                    + sp.re(Aij) * KA_re[i, j] + sp.im(Aij) * KA_im[i, j])
    Edot = sum(mm[i] ** 2 * Om ** 2 * h[i] * sp.conjugate(h[i]) for i in range(n)) / (16 * sp.pi)
    den = Edot / Om if por == "J" else Edot
    r = sp.expand(num / den)
    r = sp.series(sp.expand(r.subs(nu, (1 - delta ** 2) / 4)), v, 0, ordem_v + 1).removeO()
    r = sp.expand(sp.simplify(r))
    if racionalizar:
        r = sp.nsimplify(r, tolerance=1e-9, rational=True)
    return r


def em_s_sigma(e):
    """Reescreve uma expressao em (delta, chis, chia) nas variaveis (nu, delta, s, sigma) de Cunningham et al."""
    # chis, chia em funcao de s, sigma, delta: s = chis (1 + delta^2)/2 + chia delta ; sigma = -delta chis - chia
    S_, G_ = sp.symbols("S_ G_")
    sol = sp.solve([sp.Eq(S_, chis * (1 + delta ** 2) / 2 + chia * delta), sp.Eq(G_, -delta * chis - chia)],
                   [chis, chia], dict=True)[0]
    out = sp.expand(sp.simplify(e.subs(sol).subs({S_: s, G_: sigma})))
    return out
