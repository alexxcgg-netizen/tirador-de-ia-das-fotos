"""Revisao R1 (analitica): confere as equacoes das secoes 1 e 2 do 07_binarias_reais.md.

Tudo aqui e sympy/mpmath ou numpy leve (sem o substituto). Itens:
  A1  constantes do observavel de fase (secao 2.6): C_E, C_J e C = 2 C_E / C_J em forma fechada;
      recalibracao numerica com a fase integrada exatamente (a calibracao do exp09 usa cumsum).
  A2  coeficientes 1PN (secao 2.3): xdot a partir de E(x) e do fluxo; H22 a partir do quadrupolo 1PN.
  A3  momento angular newtoniano e divergencia Delta J (secao 1.3).
  A4  fase estacionaria (secao 2.1): |h~|^2 = a^2 Psi''/(2 pi) e a^2 Psi'' ~ Mc^(5/3) f^(-7/3) / D^2;
      a simetria PN (eta, D) -> (lambda eta, lambda D) muda |h~| por lambda^(-1/2): nao e filtro de fase.
  A5  multiplos harmonicos (secao 2.1): um filtro comum phi(w) que leve modos m = 2 e m = 3 de uma binaria
      em modos de outra binaria tem de ser linear em f (so translacao no tempo).
  A6  paridade e zeros dos harmonicos {-2}Y_l0 e {0}Y_l0 (secao 2.2, item h).
  A7  contra-exemplo a proposicao da secao 2.6: dois surtos disjuntos com fase relativa beta tem
      P(u) e Q(u) identicos e formas de onda diferentes.
Saida: resultados/revisao/rev_R1_analitico.txt
"""
import os
import sys

import numpy as np
import sympy as sp

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
from harmonicos import sYlm                              # noqa: E402
from memorias import CalculadoraMemoria                  # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1_analitico.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


th, ph, c = sp.symbols("theta phi c", real=True)


def sY(s, l, m):
    """Harmonico com peso de spin (Goldberg), simbolico em c = cos(theta), mesma convencao de harmonicos.py.

    sin(theta/2) = sqrt((1-c)/2), cos(theta/2) = sqrt((1+c)/2); a dependencia em phi e e^{i m phi}."""
    pref = (-1) ** m * sp.sqrt(sp.factorial(l + m) * sp.factorial(l - m) * (2 * l + 1)
                               / (4 * sp.pi * sp.factorial(l + s) * sp.factorial(l - s)))
    tot = 0
    sh, ch = sp.sqrt((1 - c) / 2), sp.sqrt((1 + c) / 2)
    for r in range(0, l - s + 1):
        k = r + s - m
        if k < 0 or k > l + s:
            continue
        cc = sp.binomial(l - s, r) * sp.binomial(l + s, k) * (-1) ** (l - r - s)
        p = 2 * r + s - m
        tot += cc * sh ** (2 * l - p) * ch ** p
    return sp.expand(pref * tot)


def integra_esfera_m0(f):
    """int f dOmega para f sem dependencia em phi (ja multiplicada pelos fatores de fase que se cancelam)."""
    return sp.simplify(2 * sp.pi * sp.integrate(sp.expand(f), (c, -1, 1)))


# ------------------------------------------------------------------ A1
log("== A1. Constantes do observavel de fase (secao 2.6)")
Y22, Y2m2 = sY(-2, 2, 2), sY(-2, 2, -2)
Y20s0 = sY(0, 2, 0)
Y30 = sY(-2, 3, 0)
br = integra_esfera_m0((Y22 ** 2 + Y2m2 ** 2) * Y20s0)                 # m = 0: |Y|^2 = (parte real)^2
CE = sp.nsimplify(sp.simplify(br / sp.sqrt(24)))
log("  <|Y22|^2+|Y2-2|^2, Y20> = %s ; C_E = %s = %.8f" % (sp.simplify(br), sp.simplify(br / sp.sqrt(24)),
                                                         float(br / sp.sqrt(24))))
# modo de memoria de spin: r h_x = (3/32 pi) Im(conj(H22) H22dot) sin^2 cos  (Nichols 2017, conferido no exp01 T4)
# e h_x = -Im(h30 {-2}Y30); logo |h30| = C_J |Im(conj(h22) h22dot)|
fator30 = sp.sqrt(sp.Rational(105, 2) / sp.pi) / 4
for tv in (0.3, 1.1, 2.4):                                                 # confere a forma fechada
    assert abs(float(Y30.subs(c, np.cos(tv))) - float(fator30) * np.sin(tv) ** 2 * np.cos(tv)) < 1e-12
CJ = sp.simplify(sp.Rational(3, 32) / sp.pi / fator30)
C = sp.simplify(2 * sp.simplify(br / sp.sqrt(24)) / CJ)
log("  {-2}Y30 = %s sin^2 cos ; C_J = %s = %.8f" % (fator30, CJ, float(CJ)))
log("  C = 2 C_E / C_J = %s = %.8f   (07 secao 2.6: 5,0397 ; secao 3.6: 5,039682 numerico, 'analitico 5,0396')"
    % (sp.nsimplify(C), float(C)))

# recalibracao numerica: mesma receita do exp09, mas com a fase integrada exatamente
import binarias as B                                     # noqa: E402
for nome, exata in (("fase por cumsum (exp09)", False), ("fase integrada exatamente", True)):
    t = np.arange(0, 4000, 0.25)
    T = t[-1]
    Om = 0.02 + 0.03 * t / T
    if exata:
        phi = 0.02 * t + 0.015 * t ** 2 / T
    else:
        phi = np.cumsum(Om) * 0.25
    A22 = 0.1 * (Om / 0.05) ** (2 / 3)
    h22 = A22 * np.exp(-2j * phi)
    H = np.stack([h22, np.conj(h22)], axis=1)
    Hd = B.derivada4(H, 0.25)
    calc = CalculadoraMemoria([(2, 2), (2, -2)], lmax_saida=4)
    hB, _, dmem = calc.partes_instantaneas(H, Hd, [(2, 0), (3, 0)])
    sl = slice(100, -100)
    razao = dmem[sl, 0].real / (np.abs(hB[sl, 1]) * Om[sl])
    CEn = np.median(dmem[sl, 0].real / np.abs(Hd[sl, 0]) ** 2)
    log("  calibracao numerica, %-26s: C_E = %.7f  C = %.7f  (C/C_analitico - 1 = %+.1e, dispersao %.1e)"
        % (nome, CEn, np.median(razao), np.median(razao) / float(C) - 1, np.std(razao) / np.median(razao)))

# ------------------------------------------------------------------ A2
log("")
log("== A2. Coeficientes 1PN (secao 2.3)")
x, nu = sp.symbols("x nu", positive=True)
E = -nu * x / 2 * (1 - (sp.Rational(3, 4) + nu / 12) * x)                  # M = 1, mu = nu
Fl = sp.Rational(32, 5) * nu ** 2 * x ** 5 * (1 - (sp.Rational(1247, 336) + sp.Rational(35, 12) * nu) * x)
xdot = sp.series(-Fl / sp.diff(E, x), x, 0, 7).removeO()
coef1 = sp.simplify(sp.expand(xdot / (sp.Rational(64, 5) * nu * x ** 5)).coeff(x, 1))
log("  xdot = (64/5) nu x^5 [1 + (%s) x + ...]   (07: -743/336 - 11 nu/4)" % coef1)
# quadrupolo 1PN de massa (Blanchet LRR, orbita circular): I_ij = mu { x<ij> [1 + (29/42)(1-3nu) v^2 - (1/7)(5-8nu) M/r]
#   + (11/21)(1-3nu) r^2 v<ij> } ; parte m = 2 de v<ij> = -(r w)^2/r^2 vezes a de x<ij>
gam = sp.symbols("gamma", positive=True)
fat_x = 1 + sp.Rational(29, 42) * (1 - 3 * nu) * gam - sp.Rational(1, 7) * (5 - 8 * nu) * gam
fat_v = -sp.Rational(11, 21) * (1 - 3 * nu) * gam                           # (r w)^2 = gamma em ordem newtoniana
# amplitude de d^2 I_22/dt^2 ~ mu r^2 w^2 (fat_x + fat_v); r^2 w^2 em termos de x: gamma = x (1 + (1 - nu/3) x)
r2w2 = sp.series(x ** 3 / (x * (1 + (1 - nu / 3) * x)) ** 2, x, 0, 3).removeO()
amp = sp.expand(sp.series(r2w2 * (fat_x + fat_v).subs(gam, x), x, 0, 3).removeO())
log("  H22 = 1 + (%s) x + ...   (07: -107/42 + 55 nu/42)" % sp.factor(sp.simplify(amp.coeff(x, 2))))

# ------------------------------------------------------------------ A3
log("")
log("== A3. Momento angular newtoniano e divergencia (secao 1.3)")
Mm, r = sp.symbols("M r", positive=True)
L = nu * Mm * sp.sqrt(Mm * r)                                               # mu sqrt(M r), mu = nu M
Lx = sp.simplify(L.subs(r, Mm / x))
log("  L(x) = %s  => Delta J = L(x_i) - L(x_f) = nu M^2 (x_i^-1/2 - x_f^-1/2)  [confirma]" % Lx)
# taxa de divergencia por memoria na ordem dominante (modo 22): integrando ~ eta^2 x^a, du = dx/(64/5 eta x^5)
xi = sp.symbols("x_i", positive=True)
for nome, a in (("deslocamento (|hdot|^2 ~ x^5)", 5), ("spin e giroscopica (Im(hbar hdot) ~ x^(7/2))", sp.Rational(7, 2)),
                ("int h_+^mem du (h_mem ~ x)", 1)):
    I = sp.integrate(x ** a / x ** 5, (x, xi, sp.Rational(1, 6)))
    log("  %-48s: int_xi^(1/6) x^(%s-5) dx = %s" % (nome, a, sp.simplify(I)))

# ------------------------------------------------------------------ A4
log("")
log("== A4. Fase estacionaria (secao 2.1)")
f, Mc, Dd, lam, eta = sp.symbols("f Mc D lambda eta", positive=True)
fdot = sp.Rational(96, 5) * sp.pi ** sp.Rational(8, 3) * Mc ** sp.Rational(5, 3) * f ** sp.Rational(11, 3)
Psi2 = 4 * sp.pi ** 2 / (2 * sp.pi * fdot)                                  # Psi'' = 4 pi^2/phidd, phidd = 2 pi fdot
a = (Mc / eta ** sp.Rational(3, 5)) * eta * (sp.pi * Mc / eta ** sp.Rational(3, 5) * f) ** sp.Rational(2, 3) / Dd
log("  a^2 Psi'' = %s" % sp.simplify(a ** 2 * Psi2 / (2 * sp.pi)))
# conferencia numerica de |h~|^2 = a^2 Psi''/(2 pi) para um chirp newtoniano
tt = np.linspace(-60.0, -0.5, 2 ** 21)
dtt = tt[1] - tt[0]
tau = -tt
fr = 0.5 * tau ** (-3 / 8) * 30.0                                             # f(t) newtoniano (unidades arbitrarias)
phi_t = 2 * np.pi * np.concatenate([[0], np.cumsum(0.5 * (fr[1:] + fr[:-1]) * dtt)])
amp_t = fr ** (2 / 3)
jan = np.ones_like(tt)
n_t = 20000
jan[:n_t] = 0.5 * (1 - np.cos(np.pi * np.arange(n_t) / n_t))
jan[-n_t:] = 0.5 * (1 + np.cos(np.pi * np.arange(n_t) / n_t))
hh = amp_t * jan * np.exp(-1j * phi_t)
Ht = np.fft.fft(hh) * dtt                                                    # convencao e^{-i w t}: freq positivas para e^{-i phi}? usa -f
fq = np.fft.fftfreq(len(tt), dtt)
sel = (fq < -fr.min() * 1.3) & (fq > -fr.max() / 1.6)
ff = -fq[sel]
t_f = -(ff / 15.0) ** (-8 / 3)
fdot_f = np.interp(t_f, tt, np.gradient(fr, dtt))
prev = (ff ** (2 / 3)) ** 2 / fdot_f                                          # a^2 Psi''/(2 pi) = a^2/fdot
log("  chirp numerico: mediana |h~|^2 / (a^2 Psi''/2pi) = %.4f (desvio padrao %.3f)"
    % (np.median(np.abs(Ht[sel]) ** 2 / prev), np.std(np.abs(Ht[sel]) ** 2 / prev)))
# simetria PN: a ~ eta M x / D com M fixo; Psi'' ~ 1/eta
aB2_aA2 = sp.simplify(((lam * eta) / (lam * Dd)) ** 2 / (eta / Dd) ** 2)
psiB_psiA = sp.simplify((1 / (lam * eta)) / (1 / eta))
log("  (eta, D) -> (lambda eta, lambda D), M fixo: a_B^2/a_A^2 = %s ; Psi''_B/Psi''_A = %s ; |h~_B|^2/|h~_A|^2 = %s"
    % (aB2_aA2, psiB_psiA, sp.simplify(aB2_aA2 * psiB_psiA)))
log("  => a simetria NAO e filtro de fase (muda |h~| por lambda^(-1/2) e D por lambda); D int|hdot_obs|^2 fica fixo.")

# ------------------------------------------------------------------ A5
log("")
log("== A5. Filtro comum e harmonicos m = 2, 3 (secao 2.1)")
# SPA: Psi_lm(f) = (m/2) Psi_22(2f/m) + const. Para B = filtro(A): phi(2 pi f) = (m/2) delta(2 f/m) + c_m, delta = Psi22_B - Psi22_A
# Teste: polinomio generico em f (potencias f^k, k = -5/3 ... 2) com m = 2 e m = 3
kk = [sp.Rational(-5, 3), -1, sp.Rational(-2, 3), sp.Rational(-1, 3), 0, sp.Rational(1, 3), 1, 2]
k_ = sp.symbols("k")
for m in (3, 4):
    fat = [sp.simplify(1 - sp.Rational(m, 2) * sp.Rational(2, m) ** k) for k in kk]
    log("  m = %d: coeficiente de a_k f^k em delta(f) - (m/2) delta(2f/m): %s" % (m, dict(zip([str(k) for k in kk], fat))))
log("  (k = 0 exige uma constante de fase dependente do modo, c_m = (1 - m/2) a_0, que nao e rotacao orbital)")
log("  => na base de potencias so f^1 (translacao no tempo) sobrevive. Mas a solucao geral de")
log("     delta(f) = (m/2) delta(2f/m) e delta = f p(ln f) com p periodica de periodo ln(m/2):")
fx = sp.symbols("fx", positive=True)
for m, nome in ((3, "ln(3/2)"), (4, "ln 2")):
    per = sp.log(sp.Rational(m, 2))
    lp = fx * sp.sin(2 * sp.pi * sp.log(fx) / per)
    dif = sp.lambdify(fx, lp - sp.Rational(m, 2) * lp.subs(fx, 2 * fx / m), "mpmath")
    res = "max |.| em f = 10..300 = %.1e" % max(abs(float(dif(fv))) for fv in np.linspace(10, 300, 59))
    log("     m = %d: delta = f sin(2 pi ln f / %s): delta(f) - (m/2) delta(2f/m) = %s" % (m, nome, res))
log("     com m = 2, 3 e 4 juntos os periodos ln 1.5 e ln 2 sao incomensuraveis (ln2/ln1.5 = %.6f, irracional);"
    " p continua => p constante => so translacao no tempo." % (np.log(2) / np.log(1.5)))

# ------------------------------------------------------------------ A6
log("")
log("== A6. Paridade e zeros dos harmonicos m = 0 (secao 2.2)")
for s in (-2, 0):
    for l in range(max(abs(s), 1), 6):
        Y = sp.simplify(sY(s, l, 0))
        par = sp.simplify(Y.subs(c, -c) - (-1) ** l * Y)                    # theta -> pi - theta: c -> -c
        polo = sp.simplify(Y.subs(c, 1))
        eq_ = sp.simplify(Y.subs(c, 0))
        fat = sp.factor(sp.simplify(Y / (1 - c ** 2))) if s == -2 else None
        log("  {%d}Y_%d0: Y(pi-th) - (-1)^l Y(th) = %s ; Y(0) = %s ; Y(pi/2) = %s%s"
            % (s, l, par, polo, eq_, (" ; Y/sin^2 = %s" % fat) if fat is not None else ""))
log("  => sob iota -> pi - iota: deslocamento e CM (l par) pares; spin (l impar, {-2}Y) e giroscopica (l impar, {0}Y) impares.")
log("     iota = 0: deslocamento, spin e CM se anulam (fator sin^2); giroscopica nao. iota = pi/2: spin e giro se anulam.")

# ------------------------------------------------------------------ A7
log("")
log("== A7. Contra-exemplo a proposicao da secao 2.6 (suporte desconexo)")
u = np.linspace(-600, 600, 2 ** 15)
du = u[1] - u[0]


def surto(u0):
    env = np.exp(-(u - u0) ** 2 / (2 * 40.0 ** 2))
    return env * np.exp(-0.2j * u), 0.4 * env * np.exp(-0.3j * u + 0.7j)


def montar(beta):
    a1, b1 = surto(-250.0)
    a2, b2 = surto(+250.0)
    return np.stack([a1 + np.exp(1j * beta) * a2, b1 + np.exp(1j * beta) * b2], axis=1)


H0 = montar(0.0)
H1 = montar(1.3)
dH0 = np.gradient(H0, du, axis=0)
dH1 = np.gradient(H1, du, axis=0)
P0 = np.einsum('tj,tk->tjk', dH0, dH0.conj())
P1 = np.einsum('tj,tk->tjk', dH1, dH1.conj())
Q0 = np.einsum('tj,tk->tjk', H0, dH0.conj())
Q1 = np.einsum('tj,tk->tjk', H1, dH1.conj())
sob = np.abs(np.sum(H0 * H1.conj())) / np.sqrt(np.sum(np.abs(H0) ** 2) * np.sum(np.abs(H1) ** 2))
log("  max|P1 - P0| / max|P0| = %.1e ; max|Q1 - Q0| / max|Q0| = %.1e ; |<h0, h1>| (sem maximizar fase) = %.3f"
    % (np.abs(P1 - P0).max() / np.abs(P0).max(), np.abs(Q1 - Q0).max() / np.abs(Q0).max(), sob))
log("  maximo de |h(u)| entre os surtos = %.1e (suporte praticamente desconexo)" % np.abs(H0[np.abs(u) < 20]).max())
log("  => a proposicao precisa da hipotese 'h(u) != 0 em todo o intervalo' (suporte conexo); C^1 nao basta.")

# ------------------------------------------------------------------ A8
log("")
log("== A8. Parte ordinaria do CM do codigo contra Nichols 2018, eqs. (4.25a,b) (por eta M^2 Delta x)")
from harmonicos import Dfrak as Dfr, ethb2_de_escalar as eb2          # noqa: E402
k20 = 8 * np.sqrt(np.pi / 5) * 5 / (14 * np.sqrt(6))
k40 = 8 * np.sqrt(np.pi / 5) / (504 * np.sqrt(2))
for l, k, ref in ((2, k20, -np.sqrt(5 * np.pi) / 21), (4, k40, -np.sqrt(np.pi) / 56700)):
    K = -1.5 * (2 * k / eb2(l)) / Dfr(l)
    log("  l = %d: codigo -(3/2) Dfrak^-1 Delta Phi = %.10e ; Nichols = %.10e ; razao = %.12f" % (l, K, ref, K / ref))
log("  (Nichols usa a massa M do sistema; o codigo usa M_f = M - E_rad, diferenca de 5% que e de ordem h^4)")
log("  no nivel de deformacao, so l = 2: CM_20 / J_20 = -(3/2) M / Dfrak(2) = %.4f M  (um atraso do degrau de M/2)"
    % (-1.5 / Dfr(2)))

os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(linhas) + "\n")
