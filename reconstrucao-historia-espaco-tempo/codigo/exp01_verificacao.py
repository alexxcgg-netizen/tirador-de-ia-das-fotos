"""Experimento 1: verifica o codigo das memorias contra resultados publicados.

Testes (binaria quase circular, ordem pos-newtoniana dominante, M = 1, eta = 1/4):
  T1  h^mem_20 = (4/7) sqrt(5 pi/6) eta M (x_f - x_0)            [Favata 2009]
  T2  padrao angular r h_+^mem = sin^2(17+cos^2)/(192 pi) int|H22dot|^2   [Nichols 2017]
  T3  |int h^B du|_30 = sqrt(3 pi/70) eta M^2 |x_f^-1/2 - x_0^-1/2|       [Nichols 2017]
  T4  modo de memoria de spin r h_x = (3/32 pi) Im(conj(H22) H22dot) sin^2 cos  [Nichols 2017]
  T5  momento angular irradiado pelo termo W (parte l=1) = formula de modos
  T6  calculo direto no tempo = calculo pelas matrizes de Gram
  T7  B = M2 e A = i M1 (momentos espectrais), para um pulso que se anula nas pontas
Saida: resultados/exp01_verificacao.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from harmonicos import sYlm                                     # noqa: E402
from memorias import CalculadoraMemoria, gram, momentos_espectrais, derivada  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "..", "resultados", "exp01_verificacao.txt")
linhas = []


def log(s):
    print(s)
    linhas.append(s)


# ---------------- binaria PN de ordem dominante ----------------
M, eta = 1.0, 0.25
x0, xf = 0.05, 0.20
# x(t): dx/dt = (64/5) eta x^5 / M  ->  t(x) = (5 M / 256 eta) (x0^-4 - x^-4)
tf = 5 * M / (256 * eta) * (x0 ** -4 - xf ** -4)
N = 400000
t = np.linspace(0.0, tf, N)
dt = t[1] - t[0]
x = (x0 ** -4 - 256 * eta * t / (5 * M)) ** -0.25
psi = (x0 ** -2.5 - x ** -2.5) / (32 * eta)   # psi = int x^{3/2}/M dt
# A22 = -8 sqrt(pi/5) eta M x ;  H22 = A22 exp(-2 i psi)
A = -8 * np.sqrt(np.pi / 5) * eta * M * x
xdot = 64 / 5 * eta * x ** 5 / M
Adot = -8 * np.sqrt(np.pi / 5) * eta * M * xdot
psidot = x ** 1.5 / M
H22 = A * np.exp(-2j * psi)
H22d = (Adot - 2j * A * psidot) * np.exp(-2j * psi)
lista = [(2, 2), (2, -2)]
H = np.stack([H22, np.conj(H22)], axis=1)
Hd = np.stack([H22d, np.conj(H22d)], axis=1)

calc = CalculadoraMemoria(lista)
mem = calc.memorias_tempo(H, Hd, dt)

# T1
h20 = mem["deslocamento"][(2, 0)]
esperado = 4 / 7 * np.sqrt(5 * np.pi / 6) * eta * M * (xf - x0)
log("T1 h20_mem calculado = %.6e  esperado (Favata) = %.6e  razao = %.6f" % (h20.real, esperado, h20.real / esperado))

# T2 padrao angular
th = np.linspace(0.2, 3.0, 7)
EH = np.sum(np.abs(H22d) ** 2) * dt
padrao = np.zeros_like(th)
for (l, m), c in mem["deslocamento"].items():
    padrao = padrao + np.real(c * sYlm(-2, l, m, th, 0.0))
ref = np.sin(th) ** 2 * (17 + np.cos(th) ** 2) / (192 * np.pi) * EH
log("T2 max|padrao - Nichols| / max|Nichols| = %.2e" % (np.max(np.abs(padrao - ref)) / np.max(np.abs(ref))))

# T3 memoria de spin (3,0)
s30 = mem["spin"][(3, 0)]
esp3 = np.sqrt(3 * np.pi / 70) * eta * M ** 2 * abs(xf ** -0.5 - x0 ** -0.5)
log("T3 |int h^B du|_30 = %.6e  esperado (Nichols) = %.6e  razao = %.6f  (fase de c30: %.3f pi)"
    % (abs(s30), esp3, abs(s30) / esp3, np.angle(s30) / np.pi))

# T4 modo de memoria de spin num instante
k = N // 2
hB, hEJ, dmem = calc.partes_instantaneas(H[k:k + 1], Hd[k:k + 1], [(3, 0)])
hx_calc = -np.imag(hB[0, 0] * sYlm(-2, 3, 0, th, 0.0))
hx_ref = 3 / (32 * np.pi) * np.imag(np.conj(H22[k]) * H22d[k]) * np.sin(th) ** 2 * np.cos(th)
log("T4 razao h_x(calc)/h_x(Nichols) em varios theta: %s" % np.array2string(hx_calc / hx_ref, precision=6))

# T5 momento angular
g = calc.g
Zgrid = np.zeros(g.shape, dtype=complex).ravel()
for (l, m), c in mem["Z_modos"].items():
    Zgrid = Zgrid + c * g.Y(-1, l, m).ravel()
Jz_W = -1 / (64 * np.pi) * np.sum(np.sin(g.theta).ravel() * np.imag(Zgrid) * g.peso.ravel())
Jz_modos = -1 / (16 * np.pi) * sum(mm * np.sum(np.imag(np.conj(H[:, j]) * Hd[:, j])) * dt
                                   for j, (ll, mm) in enumerate(lista))
log("T5 J_z irradiado: termo W = %.6e   formula de modos = %.6e   razao = %.6f" % (Jz_W, Jz_modos, Jz_W / Jz_modos))
E_rad = mem["energia_total"]
log("   energia irradiada = %.6e  (esperado 0.5 eta M (xf-x0) = %.6e)" % (E_rad, 0.5 * eta * M * (xf - x0)))

# T6 tempo x Gram
B, Ag = gram(H, Hd, dt)
mg = calc.memorias_gram(B, Ag)
escala = max(np.max(np.abs(np.array(list(mem[t].values())))) for t in ("deslocamento", "spin", "giroscopica"))
for tipo in ("deslocamento", "spin", "cm", "giroscopica"):
    a = np.array([mem[tipo][kk] for kk in sorted(mem[tipo])])
    b = np.array([mg[tipo][kk] for kk in sorted(mem[tipo])])
    log("T6 %-13s max|valor| = %.3e   max|tempo - Gram| / escala = %.2e"
        % (tipo, np.max(np.abs(a)), np.max(np.abs(a - b)) / escala))
log("   (a parte nula da memoria de CM e zero para uma binaria de massas iguais so com modos 22:"
    " Nichols 2018 mostra que ela exige delta m != 0 e modos (3,3), (3,1))")

# T7 momentos espectrais com um pulso que se anula nas pontas
u = np.linspace(-400, 400, 2 ** 14, endpoint=False)
du = u[1] - u[0]
env = np.exp(-u ** 2 / (2 * 60.0 ** 2))
fase = 0.15 * u + 2e-4 * u ** 2
Q = env * np.exp(-1j * fase)
Hp = np.stack([Q, 0.3 * np.conj(Q) * np.exp(0.4j)], axis=1)
Hpd = derivada(Hp, du)
Bp, Ap = gram(Hp, Hpd, du)
M1, M2 = momentos_espectrais(Hp, du)
log("T7 |B - M2|/|B| = %.2e   |A - i M1|/|A| = %.2e   |A + A^dag|/|A| = %.2e"
    % (np.abs(Bp - M2).max() / np.abs(Bp).max(), np.abs(Ap - 1j * M1).max() / np.abs(Ap).max(),
       np.abs(Ap + Ap.conj().T).max() / np.abs(Ap).max()))

# T8 parte eletrica (CM) contra as formulas de modos de Nichols 2018, eq. (DeltaK35modes),
# com U20 constante (os termos U20dot U33 que Nichols descarta somem) e V = 0.
# sinais genericos (misturas de frequencias +-w e 0), para que os produtos nao oscilem
rng = np.random.default_rng(1)
Om = 0.1
def generico():
    a, b, c = rng.normal(size=3) + 1j * rng.normal(size=3)
    return env * (a * np.exp(-1j * Om * u) + b * np.exp(1j * Om * u) + c)
U22, U31, U33 = generico(), 0.3 * generico(), 0.5 * generico()
U20 = 0.1 * np.ones_like(u)
Umod = {(2, 0): U20, (2, 2): U22, (2, -2): np.conj(U22), (3, 1): U31, (3, -1): -np.conj(U31),
        (3, 3): U33, (3, -3): -np.conj(U33)}           # U_{l,-m} = (-1)^m conj(U_lm)
lista8 = sorted(Umod)
H8 = np.stack([Umod[k] / np.sqrt(2) for k in lista8], axis=1)    # h_lm = (U_lm - i V_lm)/sqrt(2)
H8d = derivada(H8, du)
calc8 = CalculadoraMemoria(lista8)
m8 = calc8.memorias_tempo(H8, H8d, du)
Ud = {k: derivada(v, du) for k, v in Umod.items()}
I = lambda a, b: np.sum(Umod[a] * Ud[b] - Ud[a] * Umod[b]) * du       # int (U_a Udot_b - Udot_a U_b)
K33 = (np.sqrt(10) * I((3, 1), (2, 2)) - 5 * np.sum(Umod[(2, 0)] * Ud[(3, 3)]) * du) / (2880 * np.sqrt(np.pi))
K31 = (np.sqrt(10) * I((3, 3), (2, -2)) + 2 * np.sqrt(6) * I((3, -1), (2, 2))
       + 3 * np.sum(Umod[(2, 0)] * Ud[(3, 1)]) * du) / (2880 * np.sqrt(np.pi))
K55 = I((3, 3), (2, 2)) / (1680 * np.sqrt(330 * np.pi))
for nome, ref, lm in (("K33", K33, (3, 3)), ("K31", K31, (3, 1)), ("K55", K55, (5, 5))):
    c = m8["cm_potencial"][lm]
    log("T8 Delta%s: codigo = %s  Nichols = %s  razao = %s" % (nome, np.round(c, 10), np.round(ref, 10),
                                                              np.round(c / ref, 6)))

# T9 termo de helicidade da memoria giroscopica com tensores explicitos:
# C_AB = (1/2)(q_A q_B h + qbar_A qbar_B hbar), q_A = (1, i sin th), eps_(th ph) = sin th,
# Ctil_ab = eps_ca C_b^c ;  esperado N_ab Ctil^ab = -2 Im(hbar hdot).
def tensor(hc, s):
    qa = np.array([1.0, 1j * s])
    return 0.5 * (np.outer(qa, qa) * hc + np.outer(qa.conj(), qa.conj()) * np.conj(hc)).real
err9 = 0.0
for _ in range(20):
    thv = rng.uniform(0.1, 3.0)
    s = np.sin(thv)
    hv, hdv = rng.normal(size=2) + 1j * rng.normal(size=2)
    C, N = tensor(hv, s), tensor(hdv, s)
    qinv = np.diag([1.0, 1.0 / s ** 2])
    eps = np.array([[0.0, s], [-s, 0.0]])
    Cmix = C @ qinv                                   # C_b^c
    Ctil = np.einsum('ca,bc->ab', eps, Cmix)          # eps_ca C_b^c
    NC = np.einsum('ab,cd,ac,bd->', N, Ctil, qinv, qinv)
    err9 = max(err9, abs(NC - (-2 * np.imag(np.conj(hv) * hdv))))
    assert abs(Ctil[0, 1] - Ctil[1, 0]) < 1e-12        # dual de um STF e STF
log("T9 max|N_ab Ctil^ab - (-2 Im(hbar hdot))| = %.2e  (convencao eps_th_ph = +sin th)" % err9)

# giroscopica: termos separados (so informativo)
gi = mem["giroscopica"]
log("Giroscopica (r^2 Phi) modos m=0: " + ", ".join("(%d,0): %.4e%+.4ej" % (l, gi[(l, 0)].real, gi[(l, 0)].imag)
                                                   for l in range(0, 5)))
log("Helicidade integrada, parte l=0 = %.2e (zero: a helicidade dos hemisferios norte e sul se cancela)"
    % mem["helicidade_modos"][(0, 0)].real)

os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as f:
    f.write("\n".join(linhas) + "\n")
