"""Verificacao adversarial D5 (L08): EDO udot^2 = 4(uP - H^2) e unicidade pelo ponto de retorno.

Checagens independentes do relatorio linhas/L08_L09_fase_e_ringdown.md:
 1. Sinal analitico sintetico (fora do substituto): reconstrucao por exp30_comum.edo_retorno e por um integrador
    proprio (variavel w = u - H^2/P, Radau, partida pela serie de Briot-Bouquet calculada SO dos dados).
 2. Contraexemplo C^0: solucoes com quina (ramo + de t_p ate t_k > t_p, depois ramo -) tem os MESMOS P e H e
    u -> 0 nos dois lados; diferem da verdadeira depois do pico.
 3. Tabela de "contracao" do relatorio (u(t_p) errado): dependencia em delta, sinal e passos na fronteira.
 4. Passo da rede: teste (a) com dt = 0.25 e dt = 0.5 (subamostragem) -> ordem do erro.
 5. Sensibilidade a ruido suave: fracao de passos na fronteira (onde a EDO devolve o adiabatico).
 6. Expoente de amplificacao para frente: estimativa PN de ordem dominante.
Saida: codigo/revisao/ver_D5_edo.txt
"""
import os
import sys
import time
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


def salvar():
    with open(os.path.join(AQUI, "ver_D5_edo.txt"), "w") as f:
        f.write("\n".join(out) + "\n")


def edo_propria(t, P, H, t_lo, t_hi):
    """Integrador independente em w = u - u_b: wdot = s 2 sqrt(P w) - ub_dot, s = +1 antes, -1 depois de t_p.

    Partida em t_p +- ds por w = y* ds^2, com y* raiz de |ub''| = 2 y + 2 sqrt(P y) (Briot-Bouquet; so dados)."""
    dt = t[1] - t[0]
    ub = H ** 2 / P
    kp = int(np.argmax(ub))
    # parabola local de ub (5 pontos) para t_p, ub(t_p), ub''
    sl = slice(kp - 4, kp + 5)
    c = np.polyfit(t[sl] - t[kp], ub[sl], 4)
    tt = np.linspace(-dt, dt, 20001)
    k = np.argmax(np.polyval(c, tt))
    tp = t[kp] + tt[k]
    d2 = np.polyval(np.polyder(c, 2), tt[k])
    Ps = CubicSpline(t, P)
    ubd = CubicSpline(t, C.D(ub, dt))
    Pp = float(Ps(tp))
    # raiz z = sqrt(y): 2 z^2 + 2 sqrt(P) z - |d2| = 0
    z = (-2 * np.sqrt(Pp) + np.sqrt(4 * Pp + 8 * abs(d2))) / 4
    ystar = z ** 2
    ubs = CubicSpline(t, ub)

    def rhs(tq, y, s):
        w = max(y[0], 0.0)
        return [s * 2 * np.sqrt(Ps(tq) * w) - ubd(tq)]

    ds = 0.05
    res = {}
    for s, t_end in ((+1, t_lo), (-1, t_hi)):
        t0 = tp - ds if s > 0 else tp + ds
        sol = solve_ivp(rhs, (t0, t_end), [ystar * ds ** 2], args=(s,), method="Radau", rtol=1e-11,
                        atol=1e-18, dense_output=True)
        res[s] = sol
    u = np.full(len(t), np.nan)
    m1 = (t >= t_lo) & (t <= tp - ds)
    m2 = (t >= tp + ds) & (t <= t_hi)
    u[m1] = ubs(t[m1]) + res[+1].sol(t[m1])[0]
    u[m2] = ubs(t[m2]) + res[-1].sol(t[m2])[0]
    return u, tp, ystar, d2


# ====================================================================== 1. sinal sintetico
T0 = time.time()
log("== 1. Sinal analitico sintetico: a = A0 sech(t/tau)^0.5 ... (unimodal), psidot = w0 + w1 tanh(t/tau2)")
dt = 0.05
t = np.arange(-400, 400 + dt / 2, dt)
tau, tau2, w0, w1 = 40.0, 25.0, 0.30, 0.12
a = 0.4 / np.cosh(t / tau) ** 0.5
ad = -0.5 * a * np.tanh(t / tau) / tau
psid = w0 + w1 * np.tanh(t / tau2)
P = ad ** 2 + a ** 2 * psid ** 2
H = a ** 2 * psid
u_ref, kp, ncl = C.edo_retorno(t, P, H)
m = (np.abs(t) < 350)
e1 = np.abs((H / u_ref) / psid - 1)[m]
log("  exp30_comum.edo_retorno (trapezio): max |psidot/psidot_ver - 1| = %.2e (clip %d) ; adiabatico: %.2e"
    % (np.nanmax(e1), ncl, np.max(np.abs(P / H / psid - 1)[m])))
u2, tp, ys, d2 = edo_propria(t, P, H, -350, 350)
mm = m & np.isfinite(u2)
e2 = np.abs((H / u2) / psid - 1)[mm]
log("  integrador proprio (w, Radau, partida Briot-Bouquet dos dados): t_p = %.4f ; y* = %.4e (verdadeiro a^2 add^2/P"
    " = %.4e) ; max erro psidot = %.2e" % (tp, ys, (0.2 / tau ** 2) ** 2 / w0 ** 2, np.max(e2)))
# erro de passo da implementacao do relatorio
for dd in (0.1, 0.2, 0.4):
    tt = np.arange(-400, 400 + dd / 2, dd)
    aa = 0.4 / np.cosh(tt / tau) ** 0.5
    aad = -0.5 * aa * np.tanh(tt / tau) / tau
    pp = w0 + w1 * np.tanh(tt / tau2)
    uu, _, nc = C.edo_retorno(tt, aad ** 2 + aa ** 2 * pp ** 2, aa ** 2 * pp)
    mmm = np.abs(tt) < 350
    log("  edo_retorno com dt = %.2f: max erro psidot = %.2e (clip %d)" % (dd, np.nanmax(np.abs(aa ** 2 * pp / uu / pp - 1)[mmm]), nc))

# ====================================================================== 2-6 substituto, sistema A
log("")
log("== Sistema A (NRHybSur3dq8_CCE, M=65, q=1.2, chi=(0.3,-0.2), 10 Hz), modo (2,2)")
t, hh, ti = C.gerar(1.2, 0.3, -0.2)
dt = t[1] - t[0]
sel = (t >= ti - 60) & (t <= C.T_FIM + 30)
t = t[sel]
h22 = hh[(2, 2)][sel].copy()
del hh
P, H, aa, psid, psi = C.fluxos_modo(h22, dt)
uu = aa ** 2
ub = H ** 2 / P
kp = int(np.argmax(ub))
ref, _, ncl0 = C.edo_retorno(t, P, H)
log("  t_p (grade) = %.3f ; clip da referencia = %d" % (t[kp], ncl0))

# ---- 2. integrador proprio no substituto
u2, tp, ys, d2 = edo_propria(t, P, H, -3000.0, 60.0)
for nome, (lo, hi) in (("[-3000,-200]", (-3000, -200)), ("[-200,-0.1]", (-200, -0.1)), ("[0.1,30]", (0.1, 30)),
                       ("[30,60]", (30, 60))):
    mm = (t > lo) & (t < hi) & np.isfinite(u2)
    log("  integrador proprio %-13s max |psidot/ver - 1| = %.2e ; edo_retorno %.2e ; |u_proprio/u_edo - 1| max %.2e"
        % (nome, np.max(np.abs(H[mm] / u2[mm] / psid[mm] - 1)), np.max(np.abs(H[mm] / ref[mm] / psid[mm] - 1)),
           np.max(np.abs(u2[mm] / ref[mm] - 1))))
add = C.D(C.D(aa, dt), dt)
ka = int(np.argmax(aa))
log("  y* (Briot-Bouquet, dados) = %.4e ; a^2 addot^2 / P (verdade) = %.4e ; kappa = sqrt(P/y*) = %.2f ; relatorio 54.6"
    % (ys, aa[ka] ** 2 * add[ka] ** 2 / P[ka], np.sqrt(P[ka] / ys)))

# ---- 3. solucoes com quina (C^0, nao C^1)
log("")
log("== 2. Solucoes com quina: ramo + de t_p ate t_k, depois ramo - (mesmos P, H; u -> 0 nos dois lados)")


def com_quina(tk):
    """u: trapezio implicito proprio. Antes de t_p: referencia (ramo +). De t_p a t_k: ramo +. Depois: ramo -."""
    from scipy.optimize import brentq
    u = ref.copy()
    n = len(t)
    k_k = int(np.argmin(np.abs(t - tk)))

    def f(k, x, s):
        return s * 2.0 * np.sqrt(max(x * P[k] - H[k] ** 2, 0.0))
    for k in range(kp, n - 1):
        s = +1 if k < k_k else -1
        fk = f(k, u[k], s)
        uk = u[k]

        def g(x):
            return x - uk - 0.5 * dt * (fk + f(k + 1, x, s))
        lo = ub[k + 1] * (1 - 1e-15)
        if s > 0:
            hi = max(uk, ub[k + 1]) * 2 + 1e-12
            while g(hi) < 0:
                hi *= 2
            if g(lo) > 0:
                u[k + 1] = lo
                continue
        else:
            if g(lo) > 0:
                u[k + 1] = lo
                continue
            hi = max(uk, ub[k + 1]) * 1.0000001 + 1e-30
            while g(hi) < 0:
                hi = hi * 1.5 + 1e-12
        u[k + 1] = brentq(g, lo, hi, xtol=1e-17 * max(uk, 1e-30), rtol=1e-15)
    return u


fv = C.fase_acumulada(psid, t, ti, dt)
for tk in (0.5, 2.0, 5.0, 10.0):
    uq = com_quina(tk)
    psq = H / uq
    fq = C.fase_acumulada(psq, t, ti, dt)
    hq = np.sqrt(uq) * np.exp(-1j * fq)
    # P, H recalculados da curva reconstruida (longe da quina)
    hqd = C.D(hq, dt)
    Pq = np.abs(hqd) ** 2
    Hq = -np.imag(np.conj(hq) * hqd)
    long = (t > -3000) & (t < 60) & (np.abs(t - tk) > 3) & (np.abs(t - t[kp]) > 3)
    k30 = int(np.argmin(np.abs(t - 30)))
    k60 = int(np.argmin(np.abs(t - 60)))
    jan = (t > ti) & (t < 30)
    hver = aa * np.exp(-1j * fv)
    log("  t_k = %5.1f: max u/u_ver = %.3f ; |Delta fase| em t_p+30 = %.3f rad, em t_p+60 = %.3f ; max|P_rec/P-1| = %.1e,"
        " max|H_rec/H-1| = %.1e (longe das quinas) ; salto de udot na quina = %.3f u/M ; u(t_p+60)/u_ver = %.4f ;"
        " sobreposicao ate t_p+30 = %.5f"
        % (tk, np.nanmax(uq[t < 60] / uu[t < 60]), abs(fq[k30] - fv[k30]), abs(fq[k60] - fv[k60]),
           np.max(np.abs(Pq[long] / P[long] - 1)), np.max(np.abs(Hq[long] / H[long] - 1)),
           4 * np.sqrt(max(uq[np.argmin(np.abs(t - tk))] * P[np.argmin(np.abs(t - tk))] - H[np.argmin(np.abs(t - tk))] ** 2, 0)) /
           uq[np.argmin(np.abs(t - tk))], uq[k60] / uu[k60], C.overlap_fase(hq[jan], hver[jan])))
salvar()

# ---- 4. tabela de contracao do relatorio
log("")
log("== 3. u(t_p) errado (tabela de contracao do relatorio): desvio relativo de u contra a referencia")
for delta in (+1e-1, +1e-2, +1e-3, +1e-4, -1e-3, -1e-1):
    u3, _, nc = C.edo_retorno(t, P, H, u_inicial=ub[kp] * (1 + delta))
    partes = []
    for tq in (-0.25, -0.5, -1.0, -5.0, 0.25, 1.0, 5.0):
        k = int(np.argmin(np.abs(t - tq)))
        partes.append("%+.2f: %+.1e" % (tq, u3[k] / ref[k] - 1))
    # passos na fronteira nos 20 primeiros passos de cada lado
    fr_b = int(np.sum(np.abs(u3[kp - 20:kp] / ub[kp - 20:kp] - 1) < 1e-13))
    fr_f = int(np.sum(np.abs(u3[kp + 1:kp + 21] / ub[kp + 1:kp + 21] - 1) < 1e-13))
    log("  delta = %+.0e: " % delta + " ; ".join(partes) + " | clip %d ; na fronteira (20 passos antes/depois): %d/%d"
        % (nc, fr_b, fr_f))
fr_b = int(np.sum(np.abs(ref[kp - 20:kp] / ub[kp - 20:kp] - 1) < 1e-13))
fr_f = int(np.sum(np.abs(ref[kp + 1:kp + 21] / ub[kp + 1:kp + 21] - 1) < 1e-13))
log("  referencia: na fronteira (20 passos antes/depois): %d/%d ; u_ver/u_b - 1 em t_p -/+ 0.25: %.1e / %.1e"
    % (fr_b, fr_f, uu[kp - 1] / ub[kp - 1] - 1, uu[kp + 1] / ub[kp + 1] - 1))
# taxa de contracao discreta do trapezio: fator (1 - L dt/2)/(1 + L dt/2), L = 2P/udot
L = np.abs(2 * P / C.D(uu, dt))
for tq in (-10000, -1000, -100, -10, -1, -0.5):
    k = int(np.argmin(np.abs(t - tq)))
    if k <= 0:
        continue
    fac = (1 - L[k] * dt / 2) / (1 + L[k] * dt / 2)
    log("  t = %7.1f: L = 2P/|udot| = %.3g /M ; L dt = %.3g ; fator do trapezio por passo = %+.3f (exato e^{-L dt} = %.1e)"
        % (tq, L[k], L[k] * dt, fac, np.exp(-L[k] * dt)))
salvar()

# ---- 5. dt
log("")
log("== 4. Teste (a) com dt = 0.5 (subamostragem do mesmo (2,2)) contra dt = 0.25")
for passo in (1, 2):
    tt = t[::passo]
    hs = h22[::passo]
    d = tt[1] - tt[0]
    Ps_, Hs_, as_, pss, _ = C.fluxos_modo(hs, d)
    us, kps, nc = C.edo_retorno(tt, Ps_, Hs_)
    linha = []
    for nome, (lo, hi) in (("insp", (ti + 20, -200)), ("fim", (-200, 0)), ("pos", (0, 30)), ("toque", (30, 60))):
        mm = (tt > lo) & (tt < hi)
        linha.append("%s %.1e" % (nome, np.max(np.abs(Hs_[mm] / us[mm] / pss[mm] - 1))))
    log("  dt = %.2f: max erro psidot: " % d + " ; ".join(linha) + " (clip %d)" % nc)
salvar()

# ---- 6. ruido suave: passos na fronteira
log("")
log("== 5. Ruido suave 1e-3 (20 senos, 50-2000 M) em P e H: onde a EDO cai na fronteira (= adiabatico)")
rng = np.random.default_rng(30)


def pert():
    x = np.zeros(len(t))
    for _ in range(20):
        per = np.exp(rng.uniform(np.log(50), np.log(2000)))
        x += np.sin(2 * np.pi * t / per + rng.uniform(0, 2 * np.pi))
    return 1e-3 * x / np.sqrt(np.mean(x ** 2))


for amp in (1e-3, 1e-5, 1e-7):
    dP, dH = pert() * amp / 1e-3, pert() * amp / 1e-3
    Pn, Hn = P * (1 + dP), H * (1 + dH)
    un, _, nc = C.edo_retorno(t, Pn, Hn)
    ubn = Hn ** 2 / Pn
    insp = (t > ti + 20) & (t < -200)
    fim = (t > -200) & (t < 0)
    fr_i = np.mean(np.abs(un[insp] / ubn[insp] - 1) < 1e-12)
    fr_f = np.mean(np.abs(un[fim] / ubn[fim] - 1) < 1e-12)
    d_edo = np.sqrt(np.mean(((Hn / un) / psid - 1 - ((H / ref) / psid - 1))[insp] ** 2))
    d_ad = np.sqrt(np.mean(((Pn / Hn) / psid - (P / H) / psid)[insp] ** 2))
    gain = np.sqrt(np.mean(((Hn / un) / psid - 1)[fim] ** 2)), np.sqrt(np.mean(((Pn / Hn) / psid - 1)[fim] ** 2))
    log("  amplitude %.0e: clip %d ; fracao de passos na fronteira: inspiral %.3f, fim %.3f ; rms variacao psidot"
        " inspiral EDO %.2e adiab %.2e ; rms erro total no fim da inspiral EDO %.2e adiab %.2e"
        % (amp, nc, fr_i, fr_f, d_edo, d_ad, *gain))
salvar()

# ---- 7. PN: expoente de amplificacao
log("")
log("== 6. Amplificacao para frente, ordem dominante PN: int 2P/udot dt = (5/1024)/(eta^2 x^5) (de x_i ate x)")
from deteccao import MSUN_S  # noqa: E402
eta = 1.2 / 2.2 ** 2
x_i = (np.pi * 65 * MSUN_S * 10.0) ** (2 / 3)
log("  eta = %.4f ; x_i (10 Hz) = %.4f ; log10 amplificacao ~ %.3e (relatorio 1.59e5) ; taxa em x=0.0942 (t~-1000):"
    " (5/16)/(eta x) = %.2f/M (relatorio 13.26)" % (eta, x_i, (5 / 1024) / (eta ** 2 * x_i ** 5) / np.log(10),
                                                    (5 / 16) / (eta * 0.0942)))
log("tempo %.0f s" % (time.time() - T0))
salvar()
