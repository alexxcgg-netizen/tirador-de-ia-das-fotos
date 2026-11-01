"""Verificacao D5: solucoes C^0 (com quina) de udot^2 = 4(uP - H^2) com u -> 0 nos dois lados, via Radau.

Sistema A, modo (2,2). Antes de t_p: solucao verdadeira (u = |h22|^2). De t_p a t_k: ramo + que sai do ponto de
retorno tangente a fronteira (raiz sigma = +1 da serie de Briot-Bouquet). Depois de t_k: ramo -.
Tambem: familia que escapa ANTES do pico (u(t1) = (1+eps) u_ver em t1 = -30, ramo + ate t_k, depois ramo -).
Mede: P e H recalculados por diferencas finitas da curva h reconstruida (longe das quinas), erro de fase.
Saida: codigo/revisao/ver_D5_quina.txt
"""
import os
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
from scipy.interpolate import CubicSpline  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import exp30_comum as C  # noqa: E402

out = []


def log(s=""):
    print(s, flush=True)
    out.append(s)


t, hh, ti = C.gerar(1.2, 0.3, -0.2)
dt = t[1] - t[0]
sel = (t >= -400) & (t <= C.T_FIM + 30)
t = t[sel]
h22 = hh[(2, 2)][sel].copy()
del hh
P, H, aa, psid, psi = C.fluxos_modo(h22, dt)
uu = aa ** 2
ub = H ** 2 / P
kp = int(np.argmax(ub))
Ps, Hs = CubicSpline(t, P), CubicSpline(t, H)
sl = slice(kp - 4, kp + 5)
c = np.polyfit(t[sl] - t[kp], ub[sl], 4)
tt = np.linspace(-dt, dt, 20001)
tp = t[kp] + tt[np.argmax(np.polyval(c, tt))]
d2 = abs(np.polyval(np.polyder(c, 2), tp - t[kp]))
Pp = float(Ps(tp))
z_inf = (2 * np.sqrt(Pp) + np.sqrt(4 * Pp + 8 * d2)) / 4     # ramo + saindo do ponto de retorno (sigma = +1)
z_ver = (-2 * np.sqrt(Pp) + np.sqrt(4 * Pp + 8 * d2)) / 4    # solucao verdadeira (sigma = -1)
ubs = CubicSpline(t, ub)
log("t_p = %.4f ; y*(verdadeira) = %.3e ; y*(ramo + tangente) = %.3e" % (tp, z_ver ** 2, z_inf ** 2))


def rhs_u(tq, y, s):
    v = y[0] * Ps(tq) - Hs(tq) ** 2
    return [s * 2 * np.sqrt(max(v, 0.0))]


def integra(t0, u0, t1, s):
    return solve_ivp(rhs_u, (t0, t1), [u0], args=(s,), method="Radau", rtol=1e-12, atol=1e-16, dense_output=True,
                     max_step=0.05)


def avalia(trechos):
    """trechos: lista (t_a, t_b, sol); fora deles usa u verdadeiro."""
    u = uu.copy()
    for ta, tb, sol in trechos:
        m = (t >= ta) & (t <= tb)
        u[m] = sol.sol(t[m])[0]
    return u


def relata(nome, u, quinas):
    ps = H / u
    k0 = int(np.searchsorted(t, -390))
    # fase por antiderivada de spline (o trapezio de fase_acumulada tem piso ~5e-4 em P recalculado)
    fr = CubicSpline(t, ps).antiderivative()(t)
    fv = CubicSpline(t, psid).antiderivative()(t)
    fr, fv = fr - fr[k0], fv - fv[k0]
    hq = np.sqrt(u) * np.exp(-1j * fr)
    hqd = C.D(hq, dt)
    Pq = np.abs(hqd) ** 2
    Hq = -np.imag(np.conj(hq) * hqd)
    longe = (t > -380) & (t < 70)
    for q in quinas:
        longe &= np.abs(t - q) > 2.5
    k30 = int(np.argmin(np.abs(t - 30)))
    k60 = int(np.argmin(np.abs(t - 60)))
    jan = (t > -380) & (t < 30)
    hv = aa * np.exp(-1j * fv)
    log("  %-34s max u/u_ver = %8.3f ; |dfase| t_p+30 = %6.3f rad, t_p+60 = %6.3f ; max|P_rec/P-1| = %.1e ;"
        " max|H_rec/H-1| = %.1e (longe das quinas) ; u/u_ver(t_p+60) = %.5f ; sobreposicao(-380, 30) = %.5f"
        % (nome, np.max(u[t < 60] / uu[t < 60]), abs(fr[k30] - fv[k30]), abs(fr[k60] - fv[k60]),
           np.max(np.abs(Pq[longe] / P[longe] - 1)), np.max(np.abs(Hq[longe] / H[longe] - 1)), u[k60] / uu[k60],
           C.overlap_fase(hq[jan], hv[jan])))


log("")
log("1. Quina depois do pico (antes de t_p: verdadeira; t_p..t_k: ramo + tangente; depois: ramo -)")
ds = 0.05
for tk in (1.0, 3.0, 6.0, 10.0):
    s1 = integra(tp + ds, ubs(tp + ds) + z_inf ** 2 * ds ** 2, tk, +1)
    s2 = integra(tk, float(s1.y[0][-1]), C.T_FIM + 25, -1)
    u = avalia([(tp + ds, tk, s1), (tk, C.T_FIM + 25, s2)])
    m = (t > tp) & (t < tp + ds)
    u[m] = ubs(t[m]) + z_inf ** 2 * (t[m] - tp) ** 2
    relata("t_k = %.0f M" % tk, u, [tp, tk])
# referencia: solucao verdadeira pelo mesmo integrador (ramo - desde t_p + ds com a raiz verdadeira)
s0 = integra(tp + ds, ubs(tp + ds) + z_ver ** 2 * ds ** 2, C.T_FIM + 25, -1)
u = avalia([(tp + ds, C.T_FIM + 25, s0)])
relata("referencia (sem quina, Radau)", u, [tp])

log("")
log("2. Escape ANTES do pico: u(t1) = (1+eps) u_ver, ramo + desde t1 ate t_k, depois ramo -")
for t1, eps, tk in ((-30.0, 1e-9, 10.0), (-30.0, 1e-6, 5.0), (-100.0, 1e-9, 20.0)):
    k1 = int(np.argmin(np.abs(t - t1)))
    s1 = integra(t[k1], uu[k1] * (1 + eps), tk, +1)
    if s1.status != 0 or s1.t[-1] < tk - 1e-9:
        log("  t1=%g eps=%g: integracao parou em %.2f" % (t1, eps, s1.t[-1]))
        continue
    s2 = integra(tk, float(s1.y[0][-1]), C.T_FIM + 25, -1)
    u = avalia([(t[k1], tk, s1), (tk, C.T_FIM + 25, s2)])
    relata("t1=%g, eps=%g, t_k=%g" % (t1, eps, tk), u, [tk])

with open(os.path.join(AQUI, "ver_D5_quina.txt"), "w") as f:
    f.write("\n".join(out) + "\n")
