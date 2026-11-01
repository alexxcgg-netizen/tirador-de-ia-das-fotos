"""Experimento 37 (L15): a reducao de Gram e a invariancia por filtros de fase em outros campos.

Enunciado testado [D]: seja psi_j(u) (multipolos em scri+) de qualquer campo livre sem massa (qualquer spin). Todo
observavel da forma O = int du sum_jk sum_{a,b<=1} c^{ab}_jk(Omega) d^a psi_j conj(d^b psi_k) (densidade sesquilinear,
local e invariante por translacao em u) depende so de B = int psidot psidot^dag, A = int psi psidot^dag (e C = int psi
psi^dag se houver termos sem derivada) e e invariante pelo filtro comum psi~_j(w) -> e^{i phi(w)} psi~_j(w).
Casos:
  (a) campo escalar complexo sem massa e carregado: fluencia de carga Q(Omega) = -2 Im int conj(Phi) Phidot du depende
      so de Omega = A - A^dag (memoria eletromagnetica nula de Bieri-Garfinkle 2013: D^A int E_A du = 4 pi Q + ordinaria);
      fluencia de energia |Phidot|^2 -> memoria gravitacional nula (so B).
  (b) radiacao eletromagnetica (peso de spin -1): fluencia de energia -> memoria gravitacional nula (so B); a memoria EM
      LINEAR int E du = a~(w = 0) so e invariante se phi(0) = 0 (translacao sim; rotacao de dualidade constante nao).
  (c) campo massivo: memoria = int dE(w) lambda_l(beta(w)), beta = sqrt(1 - mu^2/w^2): depende do espectro inteiro (nao de
      dois momentos), mas continua invariante por filtros de fase (depende so de |psi~(w)|^2).
Saida: resultados/exp37_outros_campos.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harmonicos import Grade, modos, Dfrak, ethb2_de_escalar    # noqa: E402
from harmonicos import sYlm                                      # noqa: E402
from scipy.integrate import quad                                 # noqa: E402


def lam(l, beta):
    """coeficiente de transferencia de exp29_canais.lam (copiado, para nao executar aquele script)"""
    f = lambda x: (np.real(sYlm(0, l, 2, np.arccos(x), 0.0)) * beta ** 2 * (1 - x * x) / (2 * (1 - beta * x)))  # noqa
    return 2 * np.pi * quad(f, -1, 1, epsabs=1e-14, epsrel=1e-12, limit=400)[0]

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


rng = np.random.default_rng(37)
n_t, dt = 2 ** 14, 0.5
u = (np.arange(n_t) - n_t // 2) * dt
w = 2 * np.pi * np.fft.fftfreq(n_t, dt)


def surto(n):
    """n modos: chirps com envelope gaussiano, amplitudes e fases aleatorias (zero nas bordas)."""
    out = np.zeros((n_t, n), complex)
    for j in range(n):
        a = rng.normal() + 1j * rng.normal()
        t0 = rng.uniform(-300, 300)
        s = rng.uniform(60, 150)
        w0 = rng.uniform(0.05, 0.25)
        k = rng.uniform(-3e-4, 3e-4)
        out[:, j] = a * np.exp(-((u - t0) / s) ** 2 / 2) * np.exp(-1j * (w0 * (u - t0) + k * (u - t0) ** 2))
    return out


def filtro(H, phi):
    return np.fft.ifft(np.exp(1j * phi)[:, None] * np.fft.fft(H, axis=0), axis=0)


def dd(H):
    return np.fft.ifft(1j * w[:, None] * np.fft.fft(H, axis=0), axis=0)    # d/du (numpy: x = sum X e^{+i w u})


def fase_aleatoria():
    """fase suave aleatoria (nao impar: o campo e complexo) com dispersao forte."""
    c = rng.normal(size=6)
    x = w / np.max(np.abs(w))
    return 40 * sum(ci * np.cos((i + 1) * np.pi * x + i) for i, ci in enumerate(c)) + 900 * x ** 2


def sobreposicao(H1, H2):
    return abs(np.vdot(H1.ravel(), H2.ravel())) / np.sqrt(np.vdot(H1.ravel(), H1.ravel()).real
                                                          * np.vdot(H2.ravel(), H2.ravel()).real)


g = Grade(12, 26)
LM0 = modos(6, 0)


def proj0(F):
    _, c = g.projetar(F, 0, 6, 0)
    return np.array(c)


def memoria_grav(Fl):
    """multipolos (l >= 2) da memoria gravitacional nula de uma fluencia de energia F_lm (formula de modos do projeto)."""
    return np.array([0.5 * ethb2_de_escalar(l) * 4 * np.pi * c / Dfrak(l) if l >= 2 else 0.0
                     for (l, m), c in zip(LM0, Fl)])


# ------------------------------------------------------------------ (a) escalar carregado
log("(a) Escalar complexo carregado sem massa, l <= 3 (16 modos), filtro de fase comum aleatorio")
lista = modos(3, 0)
Ys = np.array([g.Y(0, l, m) for (l, m) in lista])
Phi = surto(len(lista))
phi = fase_aleatoria()
Phi2 = filtro(Phi, phi)


def fluencias(P):
    Pd = dd(P)
    campo = np.einsum("tj,jab->tab", P, Ys, optimize=True)
    campod = np.einsum("tj,jab->tab", Pd, Ys, optimize=True)
    Q = -2 * np.sum(np.imag(np.conj(campo) * campod), axis=0) * dt
    E = np.sum(np.abs(campod) ** 2, axis=0) * dt / (4 * np.pi)
    A = (P.T @ Pd.conj()) * dt
    Bm = (Pd.T @ Pd.conj()) * dt
    return Q, E, A, Bm


Q1, E1, A1, B1 = fluencias(Phi)
Q2, E2, A2, B2 = fluencias(Phi2)
Om1, Om2 = A1 - A1.conj().T, A2 - A2.conj().T
# Q pela matriz Omega: int conj(Phi) Phidot = sum_jk conj(A_jk) conj(Y_j) Y_k  =>  Q = i sum_jk conj(Omega_jk) conj(Y_j) Y_k
Q_om = np.real(1j * np.einsum("jk,jab,kab->ab", Om1.conj(), Ys.conj(), Ys))
log("  Q(Omega) pela matriz Omega = A - A^dag: max |Q_tempo - Q_Omega| / max|Q| = %.1e" % (
    np.max(np.abs(Q1 - Q_om)) / np.max(np.abs(Q1))))
alpha1 = np.array([-4 * np.pi * c / (l * (l + 1)) if l >= 1 else 0 for (l, m), c in zip(LM0, proj0(Q1))])
alpha2 = np.array([-4 * np.pi * c / (l * (l + 1)) if l >= 1 else 0 for (l, m), c in zip(LM0, proj0(Q2))])
mg1, mg2 = memoria_grav(proj0(E1)), memoria_grav(proj0(E2))
log("  memoria EM nula (potencial alpha_lm, l>=1): dif rel %.1e ; memoria gravitacional nula: dif rel %.1e" % (
    np.max(np.abs(alpha1 - alpha2)) / np.max(np.abs(alpha1)), np.max(np.abs(mg1 - mg2)) / np.max(np.abs(mg1))))
log("  |Delta Omega|/|Omega| = %.1e ; |Delta B|/|B| = %.1e ; sobreposicao das historias Phi x Phi_filtrado = %.3f" % (
    np.linalg.norm(Om1 - Om2) / np.linalg.norm(Om1), np.linalg.norm(B1 - B2) / np.linalg.norm(B1),
    sobreposicao(Phi, Phi2)))
# a parte hermitiana de A e termo de borda (|Phi|^2 nas pontas = 0): Q nao depende de B
log("  carga total irradiada int Q = %.6e (l = 0: nao entra na memoria EM, que tem nucleo so em l = 0)" % (
    g.integrar(Q1)))

# ------------------------------------------------------------------ (b) radiacao eletromagnetica
log()
log("(b) Radiacao eletromagnetica (peso de spin -1), 1 <= l <= 3")
lista1 = modos(3, 1)
Y1 = np.array([g.Y(-1, l, m) for (l, m) in lista1])
a = surto(len(lista1))                       # a = (E_th - i E_ph) r: multipolos do campo de radiacao


def fluencia_em(aa):
    campo = np.einsum("tj,jab->tab", aa, Y1, optimize=True)
    return np.sum(np.abs(campo) ** 2, axis=0) * dt / (4 * np.pi)


for nome, ph in [("aleatorio", fase_aleatoria()), ("translacao T=137", w * 137.0),
                 ("dualidade constante 0.6", np.full_like(w, 0.6))]:
    a2 = filtro(a, ph)
    m1, m2 = memoria_grav(proj0(fluencia_em(a))), memoria_grav(proj0(fluencia_em(a2)))
    lin1, lin2 = np.sum(a, axis=0) * dt, np.sum(a2, axis=0) * dt          # int a du = a~(0)
    log("  filtro %-24s: memoria gravitacional dif rel %.1e | memoria EM linear int a du: dif rel %.1e | sobrep. %.3f" % (
        nome, np.max(np.abs(m1 - m2)) / np.max(np.abs(m1)), np.max(np.abs(lin1 - lin2)) / np.max(np.abs(lin1)),
        sobreposicao(a, a2)))
log("  (a memoria EM linear e a~(w=0): invariante se e so se e^{i phi(0)} = 1)")

# ------------------------------------------------------------------ (c) campo massivo
log()
log("(c) Quanta massivos (massa mu = 1): memoria l=2 = int dE(w) T_2(beta(w)), T_2 = lambda_2(beta)/lambda_2(1)")
wq_ = np.linspace(1.0001, 4.0, 6000)
T2 = np.array([lam(2, np.sqrt(1 - 1 / x ** 2)) for x in wq_[::60]]) / lam(2, 1.0)
T2 = np.interp(wq_, wq_[::60], T2)


def espectro(cs, ss, pesos):
    S = sum(p * np.exp(-((wq_ - c) / s) ** 2 / 2) for c, s, p in zip(cs, ss, pesos))
    return S / np.trapezoid(S, wq_)


S1 = espectro([1.6], [0.3], [1.0])
# S2: duas linhas com os mesmos dois primeiros momentos int w S, int w^2 S (normalizado em energia)
m1_, m2_ = np.trapezoid(wq_ * S1, wq_), np.trapezoid(wq_ ** 2 * S1, wq_)
from scipy.optimize import brentq                        # noqa: E402


def S2_de(c2):
    # linhas em 1.15 e c2, pesos p e 1-p escolhidos para casar a media; depois ajusta c2 para casar o 2o momento
    c1 = 1.15
    p = (c2 - m1_) / (c2 - c1)
    return espectro([c1, c2], [0.02, 0.02], [p, 1 - p])


c2 = brentq(lambda c: np.trapezoid(wq_ ** 2 * S2_de(c), wq_) - m2_, m1_ + 0.01, 3.9)
S2 = S2_de(c2)
for nome, S in [("linha em w=1.6", S1), ("duas linhas (1.15, %.3f)" % c2, S2)]:
    log("  %-26s: int S = %.6f, <w> = %.6f, <w^2> = %.6f, memoria/E = %.6f (sem massa: 1)" % (
        nome, np.trapezoid(S, wq_), np.trapezoid(wq_ * S, wq_), np.trapezoid(wq_ ** 2 * S, wq_),
        np.trapezoid(S * T2, wq_)))
log("  => mesmos momentos espectrais de ordem 0, 1, 2 e memorias diferentes: a reducao a (B, A) falha;")
log("     um filtro de fase nao muda S(w), logo a invariancia continua valendo para a memoria final.")
with open(os.path.join(AQUI, "..", "resultados", "exp37_outros_campos.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
