"""Verificacao independente (R1v) dos itens 6, 8, 9, 10 e 11 da revisao R1 do 07 (contas curtas).

  P6  ordem PN dominante por quadratura em x (sem grade no tempo), com a CalculadoraMemoria do codigo:
      escala com eta de cada memoria e o par q = 1.2 x q = 3 com D_B = lambda D_A (exp08).
  P8  fase estacionaria: a^2 Psi'' e a simetria (eta, D) -> (lambda eta, lambda D); filtro log-periodico.
  P9  v^2 do recuo de A.
  P10 contra-exemplos a proposicao da secao 2.6 (suporte desconexo; zero isolado duplo, C^1).
  P11 constantes C_E e C do observavel de fase (sympy e codigo, sinal circular exato).
Saida: resultados/revisao/rev_R1v_analitico.txt
"""
import os
import sys

import numpy as np
import sympy as sp
from scipy.integrate import quad

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
from harmonicos import sYlm, Dfrak, ethb2_de_escalar   # noqa: E402
from memorias import CalculadoraMemoria                 # noqa: E402
import deteccao as Dt                                   # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


# ------------------------------------------------------------------ P6
K = 8 * np.sqrt(np.pi / 5)
CALC = CalculadoraMemoria([(2, 2), (2, -2)])


def mem_lo(eta, xi, xf=1 / 6, com_adot=True):
    """Memorias LO de (2, +-2) por quadratura em x: h22 = K eta x e^{-2 i psi}, xdot = 64/5 eta x^5."""
    a = lambda x: K * eta * x                              # noqa: E731
    xd = lambda x: 64 / 5 * eta * x ** 5                   # noqa: E731
    ad = lambda x: K * eta * xd(x)                         # noqa: E731
    Om = lambda x: x ** 1.5                                # noqa: E731
    op = dict(epsabs=0, epsrel=1e-13, limit=200)
    Bd = quad(lambda x: ((ad(x) ** 2 if com_adot else 0) + 4 * Om(x) ** 2 * a(x) ** 2) / xd(x), xi, xf, **op)[0]
    Are = quad(lambda x: a(x) * ad(x) / xd(x), xi, xf, **op)[0]
    Aim = quad(lambda x: 2 * Om(x) * a(x) ** 2 / xd(x), xi, xf, **op)[0]
    Bm = np.diag([Bd, Bd]).astype(complex)
    Am = np.diag([Are + 1j * Aim, Are - 1j * Aim])
    m = CALC.memorias_gram(Bm, Am)
    pre = {(2, 0): K * eta * xi * 5 / (14 * np.sqrt(6)), (4, 0): K * eta * xi / (504 * np.sqrt(2))}
    Mf = 1 - m["energia_total"] - 0.5 * eta * xi
    J = {l: m["deslocamento"][(l, 0)] + pre[(l, 0)] for l in (2, 4)}
    out = dict(J20=J[2].real, J40=J[4].real, S30=m["spin"][(3, 0)], G1=m["giroscopica"][(1, 0)].real,
               G3=m["giroscopica"][(3, 0)].real, Kn20=m["cm"][(2, 0)], Kn40=m["cm"][(4, 0)], Mf=Mf)
    for nome, MM in (("Mf", Mf), ("M", 1.0)):
        for l in (2, 4):
            out["K%d_%s" % (l, nome)] = (m["cm"][(l, 0)] - 1.5 * MM * J[l] / Dfrak(l)).real
    return out


log("P6. ordem PN dominante, quadratura em x (x_i = 0.0466, x_f = 1/6), memorias/eta")
for eta in (0.25, 1.2 / 2.2 ** 2, 0.2, 0.1875, 0.1):
    o = mem_lo(eta, 0.0466)
    log("  eta = %.4f: J20/eta = %.12f S30/eta = %.12f G1/eta = %.12f G3/eta = %.12f |K_nula| = %.0e "
        "K20(M_f)/eta = %.7f K20(M)/eta = %.7f" % (eta, o["J20"] / eta, abs(o["S30"]) / eta, o["G1"] / eta,
                                                   o["G3"] / eta, abs(o["Kn20"]) + abs(o["Kn40"]),
                                                   o["K2_Mf"] / eta, o["K2_M"] / eta))
o1, o2 = mem_lo(0.25, 0.0466, com_adot=False), mem_lo(0.1, 0.0466, com_adot=False)
log("  sem o termo adot^2: J20/eta em eta = 0.25 e 0.1: %.12f %.12f" % (o1["J20"] / 0.25, o2["J20"] / 0.1))


def obs_lo(o, iota, M, D, cm="Mf"):
    Ms, Ds = M * Dt.MSUN_S, D * Dt.MPC_S
    Y = lambda s, l: sYlm(s, l, 0, iota, 0.0).real        # noqa: E731
    d = o["J20"] * Y(-2, 2) + o["J40"] * Y(-2, 4)
    sp_ = -(o["S30"] * Y(-2, 3)).imag
    c = o["K2_" + cm] * Y(-2, 2) + o["K4_" + cm] * Y(-2, 4)
    g = o["G1"] * Y(0, 1) + o["G3"] * Y(0, 3)
    return np.array([d * Ms / Ds, sp_ * Ms * Ms / Ds, c * Ms * Ms / Ds, g * (Ms / Ds) ** 2])


M, iota = 65.0, np.radians(50.0)
xi = (np.pi * M * Dt.MSUN_S * 10.0) ** (2 / 3)
eA, eB = 1.2 / 2.2 ** 2, 3 / 16
lam = eB / eA
oA, oB = mem_lo(eA, xi), mem_lo(eB, xi)
for cm in ("Mf", "M"):
    a, b = obs_lo(oA, iota, M, 400.0, cm), obs_lo(oB, iota, M, 400.0 * lam, cm)
    log("  par q = 1.2 x q = 3 (lambda = %.4f, x_i = %.4f), CM com %-2s: (B - A)/|A| = desl %+.2e spin %+.2e CM %+.2e giro %+.4f"
        % (lam, xi, cm, *((b - a) / np.abs(a))))
log("  previsao da giroscopica: -(1/lambda - 1) = %+.4f" % (-(1 / lam - 1)))
log("  (exp08 LO: desl -1.28e-04, spin +5.94e-05, cm -5.01e-03, giro -3.22e-01)")

# ------------------------------------------------------------------ P8
log("\nP8. fase estacionaria")
f, Mc, D, eta, Mt, lamb = sp.symbols("f M_c D eta M lambda", positive=True)
x = (sp.pi * Mt * f) ** sp.Rational(2, 3)
a22 = Mt / D * 8 * sp.sqrt(sp.pi / 5) * eta * x                   # amplitude do modo (2,2)
fdot = sp.Rational(96, 5) * sp.pi ** sp.Rational(8, 3) * (eta ** sp.Rational(3, 5) * Mt) ** sp.Rational(5, 3) * f ** sp.Rational(11, 3)
Psi2 = 2 * sp.pi / fdot                                          # Psi'' = 4 pi^2/phi'' = 2 pi/fdot
expr = sp.simplify((a22 ** 2 * Psi2).subs(Mt, Mc / eta ** sp.Rational(3, 5)))
log("  a22^2 Psi'' = %s" % sp.simplify(expr))
razA = sp.simplify((a22 ** 2 * Psi2).subs({eta: lamb * eta, D: lamb * D}) / (a22 ** 2 * Psi2))
razamp = sp.simplify(a22.subs({eta: lamb * eta, D: lamb * D}) / a22)
razPsi = sp.simplify(Psi2.subs({eta: lamb * eta}) / Psi2)
log("  (eta, D) -> (lambda eta, lambda D): a_B/a_A = %s ; Psi''_B/Psi''_A = %s ; |h~_B|^2/|h~_A|^2 = %s" % (razamp, razPsi, razA))
ff = np.linspace(10, 300, 20001)
for m in (3, 4):
    per = np.log(m / 2)
    dlt = lambda z: z * np.sin(2 * np.pi * np.log(z) / per)     # noqa: E731
    log("  m = %d: delta = f sin(2 pi ln f/ln(m/2)): max|delta(f) - (m/2) delta(2f/m)| / max|delta| = %.1e" % (
        m, np.max(np.abs(dlt(ff) - m / 2 * dlt(2 * ff / m))) / np.max(np.abs(dlt(ff)))))
log("  ln 2 / ln 1.5 = %.6f" % (np.log(2) / np.log(1.5)))

# ------------------------------------------------------------------ P9
log("\nP9. (77 km/s / c)^2 = %.2e" % ((77e3 / 299792458.0) ** 2))

# ------------------------------------------------------------------ P10
log("\nP10. contra-exemplos a proposicao da secao 2.6")
u = np.linspace(-500, 500, 200001)
du = u[1] - u[0]


def bump(c, w):
    z = (u - c) / w
    out = np.zeros_like(u)
    ok = np.abs(z) < 1
    out[ok] = np.exp(-1 / (1 - z[ok] ** 2))
    return out


def PQ(H):
    Hd = np.gradient(H, du, axis=0)
    P = np.einsum("tj,tk->tjk", Hd, Hd.conj())
    Q = np.einsum("tj,tk->tjk", H, Hd.conj())
    return P, Q


b1, b2 = bump(-250, 150), bump(250, 150)
ex1 = np.exp(-1j * (0.10 * u + 2e-4 * u ** 2))
ex2 = np.exp(-1j * (0.15 * u + 3e-4 * u ** 2))
H0 = np.stack([b1 * ex1 + b2 * ex1, 0.3 * (b1 * ex2 + b2 * ex2)], axis=1)
H1 = np.stack([b1 * ex1 + np.exp(1.3j) * b2 * ex1, 0.3 * (b1 * ex2 + np.exp(1.3j) * b2 * ex2)], axis=1)
P0, Q0 = PQ(H0)
P1, Q1 = PQ(H1)
ov = abs(np.sum(H0 * H1.conj())) / np.sqrt(np.sum(np.abs(H0) ** 2) * np.sum(np.abs(H1) ** 2))
log("  (a) dois surtos de suporte compacto (C^infinito), separados por h = 0 exato; segundo surto x e^{1.3 i}:")
log("      max|P1 - P0|/max|P0| = %.1e ; max|Q1 - Q0|/max|Q0| = %.1e ; |<h0,h1>|/(|h0||h1|) (max sobre fase constante) = %.4f" % (
    np.max(np.abs(P1 - P0)) / np.max(np.abs(P0)), np.max(np.abs(Q1 - Q0)) / np.max(np.abs(Q0)), ov))
g = u ** 2 * np.exp(-(u / 120) ** 2) * np.exp(-1j * 0.1 * u)
H0 = g[:, None]
H1 = (np.sign(u) * g)[:, None]
P0, Q0 = PQ(H0)
P1, Q1 = PQ(H1)
ov = abs(np.sum(H0 * H1.conj())) / np.sum(np.abs(H0) ** 2)
log("  (b) um modo, h = u^2 e^{-(u/120)^2} e^{-0.1 i u} contra sign(u) h (C^1, so um zero isolado duplo em u = 0):")
log("      max|P1 - P0|/max|P0| = %.1e ; max|Q1 - Q0|/max|Q0| = %.1e ; |<h0,h1>|/|h0|^2 = %.1e" % (
    np.max(np.abs(P1 - P0)) / np.max(np.abs(P0)), np.max(np.abs(Q1 - Q0)) / np.max(np.abs(Q0)), ov))

# ------------------------------------------------------------------ P11
log("\nP11. constantes do observavel de fase")
th, ph = sp.symbols("theta phi", real=True)
c = sp.cos(th)
Y22 = sp.sqrt(5 / (64 * sp.pi)) * (1 + c) ** 2
Y2m2 = sp.sqrt(5 / (64 * sp.pi)) * (1 - c) ** 2
Y20 = sp.sqrt(5 / (16 * sp.pi)) * (3 * c ** 2 - 1)
ip = sp.simplify(2 * sp.pi * sp.integrate(((Y22 ** 2 + Y2m2 ** 2) * Y20 * sp.sin(th)), (th, 0, sp.pi)))
CE = sp.nsimplify(sp.simplify(ip / sp.sqrt(24)))
log("  <|Y22|^2+|Y2-2|^2, Y20> = %s ; C_E = %s = %.8f" % (sp.simplify(ip), sp.simplify(ip / sp.sqrt(24)), float(ip / sp.sqrt(24))))
Cexato = 40 * sp.sqrt(7) / 21
log("  40 sqrt(7)/21 = %.8f" % float(Cexato))
# codigo, sinal circular exato: amplitude e Omega constantes, derivada analitica
calc = CalculadoraMemoria([(2, 2), (2, -2)], lmax_saida=4)
uu = np.arange(0, 2000, 0.25)
Om0, a0 = 0.03, 0.1
h22 = a0 * np.exp(-2j * Om0 * uu)
H = np.stack([h22, np.conj(h22)], axis=1)
Hd = np.stack([-2j * Om0 * h22, np.conj(-2j * Om0 * h22)], axis=1)
hB, _, dmem = calc.partes_instantaneas(H, Hd, [(2, 0), (3, 0)])
C_cod = np.median(dmem[:, 0].real / (np.abs(hB[:, 1]) * Om0))
CE_cod = np.median(dmem[:, 0].real / np.abs(Hd[:, 0]) ** 2)
log("  codigo (circular exato): C_E = %.8f ; C = %.8f ; C/(40 sqrt7/21) - 1 = %.1e" % (CE_cod, C_cod, C_cod / float(Cexato) - 1))
# calibracao do exp09: fase por cumsum e fase exata
import binarias as Bn                                    # noqa: E402
t = np.arange(0, 4000, 0.25)
Om = 0.02 + 0.03 * t / t[-1]
for nome, phi in (("cumsum (exp09)", np.cumsum(Om) * 0.25), ("exata", 0.02 * t + 0.03 * t ** 2 / (2 * t[-1]))):
    A22 = 0.1 * (Om / 0.05) ** (2 / 3)
    h22 = A22 * np.exp(-2j * phi)
    H = np.stack([h22, np.conj(h22)], axis=1)
    Hd = Bn.derivada4(H, 0.25)
    hB, _, dmem = calc.partes_instantaneas(H, Hd, [(2, 0), (3, 0)])
    sl = slice(100, -100)
    Cn = np.median(dmem[sl, 0].real / (np.abs(hB[sl, 1]) * Om[sl]))
    log("  calibracao do exp09, fase %-15s: C = %.7f ; C/(40 sqrt7/21) - 1 = %+.1e" % (nome, Cn, Cn / float(Cexato) - 1))
with open(os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1v_analitico.txt"), "w") as fh:
    fh.write("\n".join(linhas) + "\n")
