"""Verificacao adversarial D2: alpha_2, alpha_4 em 1PN a partir de amplitudes de Blanchet (LRR) digitadas aqui
(sem usar ABFO nem o codigo do agente), Gaunt independente (formula geral de tres sYlm), fluxo 1PN como controle;
e o alpha_2 ate 2.5PN deduzido do H20 e do E de Cunningham (para ver se ha termo de cauda pi em alpha)."""
import sympy as sp
from sympy.physics.wigner import wigner_3j
import json, os

nu, x, v = sp.symbols('nu x v', positive=True)
dl = sp.Symbol('dl', positive=True)   # delta, com dl**2 = 1-4nu
I = sp.I
# Blanchet LRR (2014/2024) eqs. das amplitudes H_lm, h_lm = 2 G m nu x/(R c^2) sqrt(16 pi/5) H_lm e^{-i m psi}; ate 1PN relativo
H = {
 (2,2): 1 + v**2*(-sp.Rational(107,42) + sp.Rational(55,42)*nu),
 (2,1): I/3*dl*v,
 (3,3): -sp.Rational(3,4)*I*sp.sqrt(sp.Rational(15,14))*dl*v,
 (3,2): sp.Rational(1,3)*sp.sqrt(sp.Rational(5,7))*v**2*(1-3*nu),
 (3,1): I*dl/(12*sp.sqrt(14))*v,
 (4,4): -sp.Rational(8,9)*sp.sqrt(sp.Rational(5,7))*v**2*(1-3*nu),
 (4,2): sp.sqrt(5)/63*v**2*(1-3*nu),
}
full = {}
for (l,m),e in H.items():
    full[(l,m)] = e
    full[(l,-m)] = (-1)**l*sp.conjugate(e)

def int3(s1,l1,m1,s2,l2,m2,s3,l3,m3):
    # int sY1 sY2 sY3 dOmega, s1+s2+s3=0
    return sp.sqrt(sp.Integer((2*l1+1)*(2*l2+1)*(2*l3+1))/(4*sp.pi))*wigner_3j(l1,l2,l3,m1,m2,m3)*wigner_3j(l1,l2,l3,-s1,-s2,-s3)

def G(la,ma,lb,mb,L):
    # int (-2)Y_a conj((-2)Y_b) Y_L0 ; conj(sY_lm) = (-1)^(s+m) (-s)Y_{l,-m}
    if ma != mb: return 0
    return (-1)**(-2+mb)*int3(-2,la,ma, 2,lb,-mb, 0,L,0)

def trunc(e, n):
    e = sp.expand(e)
    return sum(e.coeff(v,k)*v**k for k in range(n+1))

num = {2:0, 4:0}; den = 0
for a,ha in full.items():
    den += a[1]**2*ha*sp.conjugate(ha)
    for b,hb in full.items():
        if a[1]!=b[1]: continue
        for L in (2,4):
            g = G(a[0],a[1],b[0],b[1],L)
            if g!=0:
                num[L] += a[1]*b[1]*ha*sp.conjugate(hb)*g
den = trunc(sp.expand(den), 2)
den0 = den.coeff(v,0)
print('fluxo relativo 1PN (sum m^2|H|^2)/lead:', sp.expand(sp.simplify(den.coeff(v,2)/den0).subs(dl**2,1-4*nu)), ' esperado: -1247/336 - 35 nu/12')
for L in (2,4):
    n = trunc(sp.expand(num[L]), 2)
    pref = 16*sp.pi*sp.sqrt(sp.factorial(L-2)/sp.factorial(L+2))
    a0 = sp.simplify(pref*n.coeff(v,0)/den0)
    r = sp.series((n/den), v, 0, 3).removeO()
    r = sp.expand(r/ r.coeff(v,0))
    print('alpha_%d: a0 =' % L, sp.nsimplify(a0), '=', sp.N(a0), '; 0.5PN:', sp.simplify(r.coeff(v,1)), '; 1PN:', sp.expand(sp.simplify(r.coeff(v,2)).subs(dl**2,1-4*nu)))
print('esperado (relatorio): alpha_2 1PN -1051/2016+71nu/24 ; alpha_4 1PN -157925/14784+9105nu/176')

# ---------- alpha_2 ate 2.5PN a partir de Cunningham: h20(x) = alpha0*int E_b' alpha, E_b = -E
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(RAIZ, 'resultados', 'exp20_pn_expressoes.json')))
s_, sg, de, M = sp.symbols('s sigma delta M', real=True)
LOC = dict(nu=nu, delta=de, s=s_, sigma=sg, x=x, M=M, pi=sp.pi, EulerGamma=sp.EulerGamma)
E = sp.sympify(d['E'], locals=LOC).subs(M,1)
H20 = sp.sympify(d['H20'], locals=LOC)
Eb = -E
# sem spin
Eb0 = sp.expand(Eb.subs({s_:0, sg:0}))
H0 = sp.expand(H20.subs({s_:0, sg:0}))
# H20 em unidades de x*{...}: razao (dH20/dx)/(dEb/dx), normalizada
y = sp.symbols('y', positive=True)
num2 = sp.diff(x*H0, x); den2 = sp.diff(Eb0, x)
rat = sp.series((num2/den2).subs(x, y**2), y, 0, 6).removeO()
rat = sp.expand(rat/rat.coeff(y,0))
for k in range(1,6):
    print('alpha_2/alpha_0 (Cunningham/E): coef de x^%s:' % sp.Rational(k,2), sp.simplify(rat.coeff(y,k)).subs(de**2, 1-4*nu))
# com spin: termos SO de alpha_2 ate 2.5PN (procura pi)
Hs = sp.expand(H20); num3 = sp.diff(x*Hs, x); den3 = sp.diff(sp.expand(Eb), x)
rat3 = sp.series((num3/den3).subs(x, y**2), y, 0, 6).removeO()
rat3 = sp.expand(rat3/rat3.coeff(y,0))
c3 = sp.expand(rat3.coeff(y,3)); c5 = sp.expand(rat3.coeff(y,5))
print('com spin, alpha_2 coef x^3/2:', sp.factor(c3))
print('com spin, alpha_2 coef x^5/2, parte com pi:', sp.factor(c5.coeff(sp.pi)))
import numpy as np
for q in (1.0, 1.2, 3.0, 8.0):
    n_ = q/(1+q)**2
    val = float(sp.N(sp.simplify(rat.coeff(y,5)).subs(nu, n_)))
    xx = 0.04
    print('q=%.1f: coef pi x^5/2 = %+.4f ; contribuicao relativa em x=0.04: %+.2e ; x=0.1: %+.2e' % (q, val, val*xx**2.5, val*0.1**2.5))
