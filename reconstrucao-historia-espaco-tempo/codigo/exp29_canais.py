"""Experimento 29 (L13): canais nao gravitacionais na memoria nula -- nucleo, exemplo degenerado e o que o quebra.

Formula de Thorne 1992 para radiacao nula (beta = 1) e particulas massivas (beta < 1), G = c = 1, h = r(h_+ - i h_x):
    D Delta h(N) = 4 int (dE/dOmega') beta^2 (n'.mbar)^2 / (1 - beta n'.N) dOmega'
(dE/dOmega' = energia, com a de repouso, por angulo solido; para beta = 1 e a formula da memoria nula).
Partes:
  (a) nucleo: fluencias l = 0 e l = 1 dao memoria zero para todo beta (equivariancia por rotacao); coeficientes de
      transferencia lambda_l(beta)/lambda_l(1) para l = 2..8 e o limite beta -> 0 (lambda_l ~ beta^l).
  (b) exemplo explicito: historia G (so ondas gravitacionais (2,+-2), energia E) x historia N (ondas com energia
      (1-eps)E + jato bipolar de neutrinos com energia eps E e a mesma forma angular + componente dipolar de um lado so,
      que da recuo). Memoria nula no ceu inteiro (l <= 8) identica.
  (c) o que quebra: (i) perfil temporal (SNR em banda de um degrau com tempo de subida tau, aLIGO e CE);
      (ii) particulas massivas (mesma fluencia com beta < 1 muda a memoria e o padrao angular);
      (iii) polarizacao: jato desalinhado do eixo das ondas da h_x na memoria, ausente no previsto pelo fluxo das ondas;
      (iv) razao memoria/oscilacao (o fluxo das ondas, medido pela parte oscilatoria, preve so (1-eps) da memoria).
Saida: resultados/exp29_canais.txt, resultados/exp29_canais.json
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import quad

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harmonicos import Grade, sYlm, modos, Dfrak, ethb2_de_escalar   # noqa: E402
from memorias import CalculadoraMemoria                              # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
linhas = []
res = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


LMAX = 8
g = Grade(60, 120)
L0 = modos(LMAX, 0)


def proj0(F):
    """F_lm = int F conj(Y_lm) (spin 0)."""
    _, c = g.projetar(F, 0, LMAX, 0)
    return dict(zip(L0, c))


def memoria_de_fluencia(F, transf=None):
    """Multipolos da memoria nula de deslocamento (em -2Y_lm) de uma fluencia F (energia/angulo solido), D = 1.
    Da formula de modos do projeto: desl_lm = (1/2) ethb2(l) (1/4)(16 pi F_lm)/Dfrak(l); transf[l] multiplica (beta<1)."""
    Fl = proj0(F)
    out = {}
    for (l, m), c in Fl.items():
        if l >= 2:
            fat = 1.0 if transf is None else transf[l]
            out[(l, m)] = fat * 0.5 * ethb2_de_escalar(l) * 4 * np.pi * c / Dfrak(l)
    return out


def no_obs(mem, th, ph):
    return sum(c * complex(sYlm(-2, l, m, th, ph)) for (l, m), c in mem.items())


# ------------------------------------------------------------------ (a) nucleo e transferencia
log("(a) Nucleo e coeficientes de transferencia")


def thorne_polo(F, beta):
    """D Dh em N = z por integracao direta do nucleo massivo (mbar = (x - i y)/sqrt2)."""
    K = beta ** 2 * np.sin(g.theta) ** 2 * np.exp(-2j * g.phi) / (2 * (1 - beta * np.cos(g.theta)))
    return 4 * g.integrar(F * K)


rng = np.random.default_rng(29)
for beta in (1.0, 0.9, 0.5, 0.1):
    # l = 0 e l = 1 em direcoes aleatorias; avaliado no polo de uma grade girada equivale a girar F
    vals = []
    for rep in range(5):
        a = rng.normal(size=4)
        n = rng.normal(size=3)
        n /= np.linalg.norm(n)
        nx = np.stack([np.sin(g.theta) * np.cos(g.phi), np.sin(g.theta) * np.sin(g.phi), np.cos(g.theta)], -1)
        F = a[0] + 3 * (nx @ n) * a[1]
        vals.append(abs(thorne_polo(F, beta)) / (abs(a[0]) + abs(a[1])))
    log("  beta=%.1f: |D Dh| / |coef| para fluencias l=0 + l=1 aleatorias (5): max %.1e" % (beta, max(vals)))


def lam(l, beta):
    """lambda_l(beta) = int Y_l2(n') beta^2 (n'.mbar)^2/(1 - beta cos) e^{2i phi}... (so a parte theta; fator 2pi)."""
    f = lambda x: (np.real(sYlm(0, l, 2, np.arccos(x), 0.0)) * beta ** 2 * (1 - x * x) / (2 * (1 - beta * x)))  # noqa
    return 2 * np.pi * quad(f, -1, 1, epsabs=1e-14, epsrel=1e-12, limit=400)[0]


betas = (1.0, 0.999, 0.99, 0.9, 0.7, 0.5, 0.3, 0.1, 0.01)
tab = {}
log("  lambda_l(beta)/lambda_l(1) (transferencia fluencia l -> memoria l; beta = velocidade das particulas):")
log("   l | " + " | ".join("b=%-5g" % b for b in betas))
for l in range(2, LMAX + 1):
    l1 = lam(l, 1.0)
    tab[l] = [lam(l, b) / l1 for b in betas]
    log("   %d | " % l + " | ".join("%.5f" % v if v > 1e-4 else "%.2e" % v for v in tab[l]))
# conferencia: lambda_l(1) contra a formula de modos (fluencia = Y_l2 + cc ... uso a grade: F = Re Y_l2)
for l in (2, 4):
    F = np.real(g.Y(0, l, 2))
    z1 = thorne_polo(F, 1.0)
    z2 = no_obs(memoria_de_fluencia(F), 0.0, 0.0)
    zb = thorne_polo(F, 0.5)
    log("  conferencia l=%d: Thorne(beta=1) %.12f%+.1ei, modos %.12f%+.1ei; Thorne(0.5)/Thorne(1) = %.10f, tabela %.10f" % (
        l, z1.real, z1.imag, z2.real, z2.imag, (zb / z1).real, lam(l, 0.5) / lam(l, 1.0)))
log("  limite beta -> 0: lambda_l(0.01)/lambda_l(1) / 0.01^l = " + ", ".join(
    "l=%d: %.4f" % (l, tab[l][-1] / 0.01 ** l) for l in range(2, LMAX + 1)))
res["transferencia"] = dict(betas=betas, tabela={str(k): v for k, v in tab.items()})

# ------------------------------------------------------------------ (b) exemplo explicito
log()
log("(b) Historia G (so ondas, (2,+-2), energia E) x historia N (ondas (1-eps)E + neutrinos eps E, jato bipolar")
log("    com a forma angular das ondas + componente dipolar de um lado so)")
lista = [(2, 2), (2, -2)]
calc = CalculadoraMemoria(lista, lmax_saida=LMAX)
E = 0.05
Bg = np.diag([1.0, 1.0]).astype(complex)
Bg *= E / (np.real(np.trace(Bg)) / (16 * np.pi))                  # energia E
mG = calc.memorias_gram(Bg, np.zeros((2, 2), complex))
eps = 0.3
mNg = calc.memorias_gram((1 - eps) * Bg, np.zeros((2, 2), complex))
# forma angular das ondas: S = (|Y22|^2 + |Y2-2|^2)/(int) ; neutrinos eps E S + dipolo
S = (np.abs(g.Y(-2, 2, 2)) ** 2 + np.abs(g.Y(-2, 2, -2)) ** 2)
S = S / g.integrar(S)
c = np.cos(g.theta)
dip_max = float(np.min(S) / np.max(np.abs(3 * c / (4 * np.pi))))  # positividade de S + d (3 cos/4pi)
d = 0.8 * dip_max
F_nu = eps * E * (S + d * 3 * c / (4 * np.pi))
log("  S(polo)/S(equador) = %.4f (polar/equatorial: jato bipolar largo); min F_nu = %.3e >= 0; dipolo d = %.4f (max %.4f)" % (
    S[0, 0] / S[np.argmin(np.abs(g.theta1 - np.pi / 2)), 0], np.min(F_nu), d, dip_max))
P_nu = float(g.integrar(F_nu * c))                                  # momento z dos neutrinos (beta = 1)
log("  energia dos neutrinos %.6f (= eps E = %.6f); momento z levado %.3e -> recuo do remanescente v = %.3e (M = 1)" % (
    g.integrar(F_nu), eps * E, P_nu, P_nu))
mNnu = memoria_de_fluencia(F_nu)
dif = []
for (l, m), v in mG["deslocamento"].items():
    if l <= LMAX:
        tot = mNg["deslocamento"][(l, m)] + mNnu.get((l, m), 0)
        dif.append(abs(tot - v))
esc = max(abs(v) for v in mG["deslocamento"].values())
log("  memoria nula, ceu inteiro (l<=8): max |N - G| / max |G| = %.2e" % (max(dif) / esc))
res["exemplo"] = dict(eps=eps, E=E, d=d, dif_rel=float(max(dif) / esc), recuo=P_nu)
# ordinaria do recuo (Thorne, particula massiva M_f com v): ~ 4 M v^2 sin^2/(1 - v cos) no maximo
log("  memoria ORDINARIA do recuo (Thorne: 4 M_f v^2 (n.mbar)^2/(1 - v.N)) ~ 2 v^2 = %.1e, contra a nula %.1e"
    " (a degenerescencia so cai em O(v^2))" % (2 * P_nu ** 2, abs(no_obs(mG["deslocamento"], np.pi / 2, 0))))

# ------------------------------------------------------------------ (c) o que quebra a degenerescencia
log()
log("(c-i) Perfil temporal: SNR (h_+) de uma memoria com subida exponencial de tempo tau, relativa ao degrau rapido")
import observaveis as O                               # noqa: E402
Dh = 1e-22
fs = 4096.0
tt = np.arange(-8.0, 8.0, 1 / fs)
tab_t = {}
for nome in ("aLIGO", "CE"):
    ref = None
    out = []
    for tau in (1e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0):
        s = np.where(tt > 0, Dh * (1 - np.exp(-np.clip(tt, 0, None) / tau)), 0.0)
        rho = O.snr2(tt, s.astype(complex), nome, 10.0)
        if ref is None:
            ref = rho
        out.append((tau, rho, rho / ref))
    tab_t[nome] = out
    log("  %s: " % nome + "; ".join("tau=%g s: %.3g (%.3f)" % x for x in out))
res["perfil"] = {k: [list(map(float, x)) for x in v] for k, v in tab_t.items()}
log("  => neutrinos emitidos em ~1 s (supernova) quase nao aparecem em banda; so a fracao com subida de ms compete.")

log()
log("(c-ii) Particulas massivas: o mesmo F_nu emitido como particulas com beta < 1 (mesma energia total)")
for beta in (0.99, 0.9, 0.5):
    tr = {l: lam(l, beta) / lam(l, 1.0) for l in range(2, LMAX + 1)}
    mb = memoria_de_fluencia(F_nu, tr)
    zN = no_obs({k: mNg["deslocamento"][k] + mNnu.get(k, 0) for k in mNg["deslocamento"]}, np.pi / 2, 0)
    zb = no_obs({k: mNg["deslocamento"][k] + mb.get(k, 0) for k in mNg["deslocamento"]}, np.pi / 2, 0)
    z0 = no_obs({k: mNg["deslocamento"][k] + mb.get(k, 0) for k in mNg["deslocamento"]}, np.radians(30), 0)
    zN0 = no_obs({k: mNg["deslocamento"][k] + mNnu.get(k, 0) for k in mNg["deslocamento"]}, np.radians(30), 0)
    log("  beta=%.2f: memoria de lado (iota=90) %.6e contra %.6e (beta=1): razao %.5f; em iota=30: razao %.5f"
        " (padrao angular muda: razoes diferentes)" % (beta, zb.real, zN.real, zb.real / zN.real, z0.real / zN0.real))

log()
log("(c-iii) Polarizacao: jato bipolar estreito (meia abertura 15 graus) de neutrinos, eixo inclinado de alpha do eixo")
log("        das ondas, fora do plano (z, N); observador iota = 60 graus. psi = (1/2) arg(Dh_+ - i Dh_x)")
th_o = np.radians(60.0)
nx = np.stack([np.sin(g.theta) * np.cos(g.phi), np.sin(g.theta) * np.sin(g.phi), np.cos(g.theta)], -1)
tabp = []
for adeg in (0, 15, 30, 60, 90):
    a = np.radians(adeg)
    eixo = np.array([0.0, np.sin(a), np.cos(a)])                      # inclinado no plano (y, z); N no plano (x, z)
    cosj = nx @ eixo
    Fj = (np.abs(cosj) > np.cos(np.radians(15.0))).astype(float)
    Fj = eps * E * Fj / g.integrar(Fj)
    mj = memoria_de_fluencia(Fj)
    zg = no_obs(mNg["deslocamento"], th_o, 0.0)
    zj = no_obs(mj, th_o, 0.0)
    zt = zg + zj
    psi = 0.5 * np.degrees(np.angle(zt))
    tabp.append((adeg, zg.real, zj.real, zj.imag, psi))
    log("  alpha=%2d: ondas Dh_+=%.4e | jato Dh_+=%+.4e Dh_x=%+.4e | total psi = %+.3f graus (ondas sozinhas: 0)" % (
        adeg, zg.real, zj.real, -zj.imag, psi))
res["polarizacao"] = tabp
log("  nota: a memoria nula e sempre de paridade eletrica (E) para qualquer canal; o que separa canais e a ORIENTACAO")
log("  do padrao, isto e, o angulo de polarizacao da memoria relativo ao previsto pelo fluxo das ondas.")

log()
log("(c-iv) Razao memoria/oscilacao: o fluxo das ondas (medido pela parte oscilatoria) preve so a parte das ondas")
zg = no_obs(mG["deslocamento"], np.pi / 2, 0).real
zn = no_obs(mNg["deslocamento"], np.pi / 2, 0).real
log("  de lado: memoria observada (G e N) %.5e; prevista pelo fluxo das ondas: G %.5e, N %.5e -> excesso em N %.3f"
    % (zg, zg, zn, zg / zn - 1))
log("  excesso minimo de energia nao gravitacional pela desigualdade (c_inf = 4): E_x >= D |excesso| / 4 = %.4f"
    " (verdadeiro %.4f; razao %.3f)" % (abs(zg - zn) / 4, eps * E, abs(zg - zn) / 4 / (eps * E)))
with open(os.path.join(RES, "exp29_canais.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(RES, "exp29_canais.json"), "w") as f:
    json.dump(res, f, indent=1, default=float)
