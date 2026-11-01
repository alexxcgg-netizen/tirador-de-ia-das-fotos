"""Verificacao D2: (1) J(x) pela primeira lei a partir do E(x) de Cunningham contra o J de Blanchet (digitado aqui);
(2) serie S30(x) a partir de beta_3 (coeficientes do relatorio) e E_b; (3) H20 a partir de alpha_2 e E_b."""
import json, os
import sympy as sp
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(RAIZ, 'resultados', 'exp20_pn_expressoes.json')))
nu, x = sp.symbols('nu x', positive=True)
s_, sg, de, M = sp.symbols('s sigma delta M', real=True)
LOC = dict(nu=nu, delta=de, s=s_, sigma=sg, x=x, M=M, pi=sp.pi, EulerGamma=sp.EulerGamma)
E = sp.sympify(d['E'], locals=LOC).subs(M, 1)
Eb = sp.expand(-E)
y = sp.symbols('y', positive=True)
# J_orb: dJ = dE/Omega, Omega = x^{3/2}; J = int x^{-3/2} dE/dx dx (E = -E_b, J decresce com x)
integrando = sp.expand(sp.diff(E, x) * x**sp.Rational(-3, 2))
J = sp.integrate(integrando, x)
J0 = sp.expand(J.subs({s_: 0, sg: 0}))
Jbl = nu * x**sp.Rational(-1, 2) * (1 + (sp.Rational(3, 2) + nu/6)*x + (sp.Rational(27, 8) - sp.Rational(19, 8)*nu + nu**2/24)*x**2
       + (sp.Rational(135, 16) + (-sp.Rational(6889, 144) + sp.Rational(41, 24)*sp.pi**2)*nu + sp.Rational(31, 24)*nu**2 + sp.Rational(7, 1296)*nu**3)*x**3)
dif = sp.expand(J0 - Jbl)
dv = sp.expand((dif*x**sp.Rational(1,2)).subs(x, y**2)/nu)
print('J(primeira lei, sem spin) - J(Blanchet), coeficientes ate x^3 relativos:', [sp.simplify(dv.coeff(y, k)) for k in range(0, 7)])
Jso = sp.expand(J - J0)
jv = sp.expand((Jso*x**sp.Rational(1,2)/nu).subs(x, y**2))
print('J SO relativo: x^{3/2}', sp.factor(jv.coeff(y,3)), '; x^{5/2}', sp.factor(jv.coeff(y,5)))
# S30 a partir de beta_3 (relatorio) e E_b ate 1.5PN
b2 = -sp.Rational(725, 4536) + sp.Rational(145, 54)*nu
b3 = sp.Rational(100, 27)*s_ + sp.Rational(1415, 432)*de*sg
beta = 1 + b2*x + b3*x**sp.Rational(3, 2)
dSdx = -beta * x**sp.Rational(-3, 2) * sp.diff(Eb, x)
S = sp.integrate(sp.expand(dSdx), x)
Sr = sp.expand((S*x**sp.Rational(1,2)/nu).subs(x, y**2))
print('S30/(beta0 nu x^-1/2): 0', Sr.coeff(y,0), '; 1PN', sp.expand(Sr.coeff(y, 2)), '; 1.5PN', sp.expand(Sr.coeff(y, 3)))
print('   relatorio: 7529/4536-68nu/27 ; -(415s/54+3575 delta sigma/864)')
