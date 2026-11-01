"""Verificacao adversarial D4 (L13, L15): limite beta -> 0 dos coeficientes lambda_l(beta), cota |K_beta| <= 1,
e o contraexemplo massivo de exp37 (c).

(1) Forma fechada: com F = Y_l2 no referencial de N, lambda_l(beta) = 2 pi int P_l^2-normalizado * beta^2 (1-x^2) /
    (2 (1 - beta x)) dx. Expandindo 1/(1-beta x) = sum beta^k x^k e usando que (1-x^2) x^k esta no espaco gerado por
    P_n^2 com n <= k+2, o primeiro termo nao nulo e k = l-2:
       lambda_l(beta)/lambda_l(1) -> c_l beta^l,  c_l = int (1-x^2) x^(l-2) P_l^2 dx / int (1+x) P_l^2 dx.
    sympy exato para l = 2..10; conferencia com mpmath (50 algarismos) em beta = 0.01, e contra a tabela de exp29
    (que usa quad em precisao dupla: l = 6..8 em beta = 0.01 ficam abaixo do arredondamento).
(2) |K_beta| = beta^2 (1-x^2) / (2 (1 - beta x)) <= (1+x)/2 <= 1 numa grade densa de (beta, x).
(3) exp37 (c): os dois espectros casam int S, int w S, int w^2 S, mas NAO necessariamente int S/w (que e o analogo de A
    para um modo); construo um par que casa int S, int S/w e int w S (B, A e um momento a mais) e mostro que a memoria
    difere.
"""
import numpy as np
import sympy as s
import mpmath as mp
from scipy.integrate import quad
from scipy.optimize import brentq, fsolve

x = s.symbols("x", real=True)
print("(1) c_l exato (sympy)")
cl = {}
for l in range(2, 11):
    P = s.assoc_legendre(l, 2, x)
    num = s.integrate(s.expand((1 - x ** 2) * x ** (l - 2) * P), (x, -1, 1))
    den = s.integrate(s.expand((1 + x) * P), (x, -1, 1))
    cl[l] = s.nsimplify(s.simplify(num / den))
    # conferencia em alta precisao: lambda_l(beta)/lambda_l(1)/beta^l em beta = 1e-3
    Pf = s.lambdify(x, P, "mpmath")
    mp.mp.dps = 60
    b = mp.mpf("1e-3")
    lb = mp.quad(lambda t: Pf(t) * b ** 2 * (1 - t * t) / (2 * (1 - b * t)), [-1, 1])
    l1 = mp.quad(lambda t: Pf(t) * (1 + t) / 2, [-1, 1])
    print("  l=%2d: c_l = %-12s = %.10f ; mpmath (beta=1e-3) %.10f" % (l, cl[l], float(cl[l]), float(lb / l1 / b ** l)))
# formula fechada candidata
print("  candidatos: 4/5, 4/7, 8/21, 8/33 (D4); razoes sucessivas c_{l+1}/c_l:",
      ", ".join(str(s.nsimplify(cl[l + 1] / cl[l])) for l in range(2, 10)))
lg = s.symbols("l", integer=True, positive=True)
cand = lambda l: s.Integer(2) ** l * s.factorial(l) * s.factorial(l + 2) / s.factorial(2 * l + 1) / 6  # noqa: E731
print("  teste da forma 2^l l! (l+2)! / (6 (2l+1)!):", all(s.simplify(cand(l) - cl[l]) == 0 for l in range(2, 11)))

print("  exp29 em beta = 0.01 (quad em dupla) contra o exato x (1 + O(beta^2)):")
from_exp29 = {6: 0.1492, 7: 0.0895, 8: 0.0421}


def lam_dupla(l, beta):
    Pf = s.lambdify(x, s.assoc_legendre(l, 2, x), "numpy")
    f = lambda t: Pf(t) * beta ** 2 * (1 - t * t) / (2 * (1 - beta * t))   # noqa: E731
    return quad(f, -1, 1, epsabs=1e-14, epsrel=1e-12, limit=400)[0]


for l in (5, 6, 7, 8):
    exato = float(cl[l])
    print("   l=%d: exp29 %s ; quad dupla refeito %.4f ; exato %.4f" % (
        l, from_exp29.get(l, "0.2424"), lam_dupla(l, 0.01) / lam_dupla(l, 1.0) / 0.01 ** l, exato))

print()
print("(2) |K_beta| <= (1+x)/2 <= 1 e monotonia em beta")
bb, xx = np.meshgrid(np.linspace(0, 1, 2001), np.linspace(-1, 1, 2001), indexing="ij")
Kb = bb ** 2 * (1 - xx ** 2) / (2 * (1 - bb * xx + 1e-300))
Kb[(bb == 1) & (xx == 1)] = 1.0
print("  max (|K_beta| - (1+x)/2) = %.2e ; max |K_beta| = %.6f ; monotonia: min d|K|/dbeta = %.2e" % (
    np.max(Kb - (1 + xx) / 2), np.max(Kb), np.min(np.diff(Kb, axis=0))))

print()
print("(3) exp37 (c): espectros massivos (mu = 1)")


def lam2(beta):
    f = lambda t: 3 * (1 - t * t) * beta ** 2 * (1 - t * t) / (2 * (1 - beta * t))   # noqa: E731
    return quad(f, -1, 1, epsabs=1e-15, epsrel=1e-13)[0]


L21 = lam2(1.0)
wq = np.linspace(1.0001, 4.0, 6000)
T2 = np.array([lam2(np.sqrt(1 - 1 / w ** 2)) for w in wq]) / L21


def espectro(cs, ss, pesos):
    S = sum(p * np.exp(-((wq - c) / sg) ** 2 / 2) for c, sg, p in zip(cs, ss, pesos))
    return S / np.trapezoid(S, wq)


def mom(S):
    return dict(E=np.trapezoid(S, wq), inv=np.trapezoid(S / wq, wq), m1=np.trapezoid(wq * S, wq),
                m2=np.trapezoid(wq ** 2 * S, wq), mem=np.trapezoid(S * T2, wq))


S1 = espectro([1.6], [0.3], [1.0])
m1_, m2_ = mom(S1)["m1"], mom(S1)["m2"]


def S2_de(c2):
    c1 = 1.15
    p = (c2 - m1_) / (c2 - c1)
    return espectro([c1, c2], [0.02, 0.02], [p, 1 - p])


c2 = brentq(lambda c: mom(S2_de(c))["m2"] - m2_, m1_ + 0.01, 3.9)
S2 = S2_de(c2)
for nome, S in (("D4 linha larga", S1), ("D4 duas linhas", S2)):
    m = mom(S)
    print("  %-16s: int S %.6f | int S/w %.6f | <w> %.6f | <w^2> %.6f | memoria/E %.6f" % (
        nome, m["E"], m["inv"], m["m1"], m["m2"], m["mem"]))
# par que casa E, int S/w (analogo de A) e <w>: tres linhas estreitas com pesos e uma posicao livres
alvo = mom(S1)


def S3_de(par):
    p1, p2, c3 = par
    return espectro([1.2, 1.9, c3], [0.02, 0.02, 0.02], [p1, p2, 1 - p1 - p2])


def resid(par):
    m = mom(S3_de(par))
    return [m["inv"] - alvo["inv"], m["m1"] - alvo["m1"], m["m2"] - alvo["m2"]]


sol = fsolve(resid, [0.4, 0.3, 2.5], full_output=True)
S3 = S3_de(sol[0])
m3 = mom(S3)
print("  par novo (3 linhas %s): int S %.6f | int S/w %.6f | <w> %.6f | <w^2> %.6f | memoria/E %.6f | pesos ok: %s" % (
    np.array2string(sol[0], precision=4), m3["E"], m3["inv"], m3["m1"], m3["m2"], m3["mem"],
    bool(min(sol[0][0], sol[0][1], 1 - sol[0][0] - sol[0][1]) > 0)))
print("  diferenca de memoria (linha larga x par novo, mesmos int S, int S/w, <w>, <w^2>): %.3e relativo" % (
    abs(m3["mem"] - alvo["mem"]) / alvo["mem"]))

print()
print("(3b) par com pesos lineares: 4 linhas estreitas em posicoes fixas, pesos resolvem int S, int S/w, <w>, <w^2>")
for pos in ([1.15, 1.45, 1.9, 2.4], [1.05, 1.5, 2.0, 2.6], [1.3, 1.5, 1.8, 2.2]):
    linhas_ = [espectro([c], [0.02], [1.0]) for c in pos]
    Mlin = np.array([[mom(Sk)[k] for Sk in linhas_] for k in ("E", "inv", "m1", "m2")])
    pesos = np.linalg.solve(Mlin, np.array([alvo[k] for k in ("E", "inv", "m1", "m2")]))
    S4 = sum(p * Sk for p, Sk in zip(pesos, linhas_))
    m4 = mom(S4)
    print("  posicoes %s: pesos %s (>=0: %s) | int S/w %.6f (alvo %.6f) | memoria/E %.6f contra %.6f: dif %.2e" % (
        pos, np.array2string(pesos, precision=4), bool(np.all(pesos >= 0)), m4["inv"], alvo["inv"], m4["mem"],
        alvo["mem"], abs(m4["mem"] - alvo["mem"]) / alvo["mem"]))
print("  forma fechada c_l = 2^(l-1) l! (l+2)! / (2l+1)!:",
      all(s.simplify(s.Integer(2) ** (l - 1) * s.factorial(l) * s.factorial(l + 2) / s.factorial(2 * l + 1) - cl[l]) == 0
          for l in range(2, 11)))

print()
print("(3c) so (B, A) <-> (int S, int S/w) casados: 2 linhas estreitas em (c1, c2), pesos pela restricao linear")
for pos in ([1.15, 2.4], [1.3, 2.0], [1.05, 3.0]):
    linhas_ = [espectro([c], [0.02], [1.0]) for c in pos]
    Mlin = np.array([[mom(Sk)[k] for Sk in linhas_] for k in ("E", "inv")])
    pesos = np.linalg.solve(Mlin, np.array([alvo[k] for k in ("E", "inv")]))
    S5 = sum(p * Sk for p, Sk in zip(pesos, linhas_))
    m5 = mom(S5)
    print("  posicoes %s: pesos %s | memoria/E %.6f contra %.6f: dif %.2e" % (
        pos, np.array2string(pesos, precision=4), m5["mem"], alvo["mem"], abs(m5["mem"] - alvo["mem"]) / alvo["mem"]))
