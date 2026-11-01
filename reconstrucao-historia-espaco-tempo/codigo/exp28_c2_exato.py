"""Experimento 28 (L12): c_2 em forma fechada (sympy). Gamma_jk = (1/4pi) int Y_j conj(Y_k) (1+cos th)/2 e^{-2i phi},
modos l = 2, harmonicos -2Y_2m explicitos; maior autovalor de (X + X^T)/2, X = Gamma^T, vezes 16 pi.
Saida: resultados/exp28_c2_exato.txt"""
import os
import sympy as s

th, ph = s.symbols("theta phi", real=True)
x = s.symbols("x", real=True)
# -2Y_2m (convencao de harmonicos.py / SXS), em termos de theta (phi fatorado)
Y = {2: s.sqrt(5 / (64 * s.pi)) * (1 + s.cos(th)) ** 2,
     1: s.sqrt(5 / (16 * s.pi)) * s.sin(th) * (1 + s.cos(th)),
     0: s.sqrt(15 / (32 * s.pi)) * s.sin(th) ** 2,
     -1: s.sqrt(5 / (16 * s.pi)) * s.sin(th) * (1 - s.cos(th)),
     -2: s.sqrt(5 / (64 * s.pi)) * (1 - s.cos(th)) ** 2}
ms = [-2, -1, 0, 1, 2]
n = len(ms)
G = s.zeros(n, n)
for a, mj in enumerate(ms):
    for b, mk in enumerate(ms):
        if mj == mk + 2:
            integ = s.integrate(Y[mj] * Y[mk] * (1 + s.cos(th)) / 2 * s.sin(th), (th, 0, s.pi)) * 2 * s.pi
            G[a, b] = s.simplify(integ / (4 * s.pi))
X = G.T
H = (X + X.T) / 2
ev = [s.nsimplify(s.simplify(e * 16 * s.pi)) for e in H.eigenvals()]
out = ["Gamma (l=2, ordem m = -2..2):", str(G), "autovalores de 16 pi (X+X^T)/2: " + str(ev),
       "c_2 = max = " + str(max(ev, key=lambda e: float(e))) + " = %.15f" % float(max(ev, key=lambda e: float(e)))]
# conferencia numerica dos harmonicos contra harmonicos.sYlm
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harmonicos import sYlm          # noqa: E402
err = max(abs(complex(sYlm(-2, 2, m, 0.77, 0.0)) - float(Y[m].subs(th, 0.77))) for m in ms)
out.append("conferencia -2Y_2m contra harmonicos.sYlm em theta = 0.77: %.1e" % err)
print("\n".join(out))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", "exp28_c2_exato.txt"), "w").write(
    "\n".join(out) + "\n")
