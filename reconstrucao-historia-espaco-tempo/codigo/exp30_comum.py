"""Ferramentas comuns da linha L08 (agente D5): recuperacao da fase de um modo a partir de P = |hdot|^2 e
H = -Im(conj(h) hdot), e os fluxos projetados nos modos de memoria.

Para um modo h = a exp(-i psi):
    P = adot^2 + a^2 psidot^2,   H = a^2 psidot,   u = a^2  =>  udot^2 = 4 (u P - H^2),   psidot = H / u.
(Identidade: conj(h) hdot = udot/2 - i H, e |conj(h) hdot|^2 = u P.)

Tres reconstrucoes de (u, psidot) a partir de (P, H):
  adiabatica  psidot = P / H (o estimador Omega = P/(2H) do exp09, aqui para psidot = 2 Omega);
  iteracao    psidot_{n+1} = (P - adot_n^2) / H com a_n^2 = H / psidot_n (converge antes do pico; diverge depois);
  edo         udot = +-2 sqrt(uP - H^2) integrada por trapezio implicito a partir do ponto de retorno
              t_p = argmax(H^2/P), onde u(t_p) = H^2/P (t_p): para tras no ramo + (antes do pico) e para frente
              no ramo - (depois). Sao as direcoes estaveis; a integracao para frente desde o passado e
              exponencialmente instavel (taxa 2P/udot).
Fluxos dos modos de memoria (nivel A, todos os modos oscilatorios do substituto, via exp24_comum.taxas_m0):
    P_mem = Re(d h20^mem/du) / C_E,   H_mem = Im(h30^B) / C_J,
    C_E = sqrt30/(42 sqrtpi), C_J = sqrt210/(280 sqrtpi)   (com so o par (2,+-2) as duas sao exatas).
Modos m = 0 de RN (substituto): P_rn = d Re(h20)/du / C_E,  H_rn = Im(h30) / C_J.
"""
import os
import sys

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import binarias as B                                     # noqa: E402
import observaveis as O                                  # noqa: E402
from deteccao import MSUN_S                               # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
FIG = os.path.join(AQUI, "..", "figuras")
C_E = np.sqrt(30) / (42 * np.sqrt(np.pi))
C_J = np.sqrt(210) / (280 * np.sqrt(np.pi))
COR = dict(azul="#2a78d6", laranja="#eb6834", verde="#1baf7a", texto="#52514e", fundo="#fcfcfb", grade="#e6e5e0",
           cinza="#9a9890")
T_FIM = 60.0          # depois de ~65 M o (2,2) do substituto deixa de ser um modo de frequencia positiva limpo


def estilo(plt):
    plt.rcParams.update({"figure.facecolor": COR["fundo"], "axes.facecolor": COR["fundo"],
                         "axes.edgecolor": "#c9c8c2", "axes.labelcolor": COR["texto"],
                         "xtick.color": COR["texto"], "ytick.color": COR["texto"], "text.color": COR["texto"],
                         "axes.grid": True, "grid.color": COR["grade"], "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False})


def D(y, dt):
    """Derivada de 8a ordem de um vetor (observaveis.derivada)."""
    return O.derivada(np.asarray(y)[:, None], dt)[:, 0]


def fluxos_modo(h22, dt):
    """P, H, a, psidot verdadeiros de um modo."""
    hd = D(h22, dt)
    P = np.abs(hd) ** 2
    H = -np.imag(np.conj(h22) * hd)
    psi = -np.unwrap(np.angle(h22))
    return P, H, np.abs(h22), D(psi, dt), psi


def fluxos_memoria(t, h, so22=False):
    """(P_mem, H_mem) pelas leis de balanco (nivel A) e as taxas completas (R, HB), L = 2..8, m = 0."""
    import exp24_comum as X
    dt = t[1] - t[0]
    Losc = B.lista_osc()
    Hm = np.stack([h[k] for k in Losc], axis=1)
    if so22:
        mask = np.array([k in ((2, 2), (2, -2)) for k in Losc])
        Hm = Hm * mask[None, :]
    Hd = O.derivada(Hm, dt)
    R, HB = X.taxas_m0(Hm, Hd)
    del Hm, Hd
    return R[:, 0].real / C_E, HB[:, 1].imag / C_J, R, HB


def fluxos_rn(t, h):
    dt = t[1] - t[0]
    return D(h[(2, 0)].real, dt) / C_E, h[(3, 0)].imag / C_J


# ------------------------------------------------------------------ reconstrucoes
def adiabatica(P, H):
    return P / H


def iteracao(P, H, dt, n=40, mascara=None):
    """psidot pela iteracao de ponto fixo; devolve (psidot, historico da maior variacao relativa por passo)."""
    psid = P / H
    hist = []
    for _ in range(n):
        with np.errstate(invalid="ignore", divide="ignore"):
            a = np.sqrt(H / psid)
            novo = (P - D(a, dt) ** 2) / H
            var = np.abs(novo / psid - 1)
        if mascara is not None:
            var = var[mascara]
        hist.append(float(np.nanmax(var)) if np.any(np.isfinite(var)) else np.nan)
        psid = novo
    return psid, hist


def ponto_retorno(P, H):
    """Indice do maximo de u_b = H^2/P e o valor de u_b; refinamento parabolico do instante."""
    ub = np.where(P > 0, H ** 2 / np.where(P > 0, P, 1.0), 0.0)
    kp = int(np.argmax(ub))
    y0, y1, y2 = ub[kp - 1], ub[kp], ub[kp + 1]
    frac = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    return kp, ub, frac


def edo_retorno(t, P, H, kp=None, u_inicial=None, ramo_depois=-1):
    """u(t) de udot^2 = 4(uP - H^2) por trapezio implicito a partir do ponto de retorno kp.

    Para tras (ramo +, estavel antes do pico) e para frente (ramo ramo_depois; -1 = o fisico). u_inicial: valor
    em kp (padrao H^2/P em kp). Devolve (u, kp, nclip): nclip = passos em que o trapezio caiu na fronteira
    u = H^2/P (sem raiz real).
    """
    dt = t[1] - t[0]
    ub = np.where(P > 0, H ** 2 / np.where(P > 0, P, 1.0), 0.0)
    if kp is None:
        kp = int(np.argmax(ub))
    n = len(t)
    u = np.full(n, np.nan)
    u[kp] = ub[kp] if u_inicial is None else u_inicial
    nclip = 0

    def f(k, x, s):
        return s * 2.0 * np.sqrt(max(x * P[k] - H[k] ** 2, 0.0))

    for k in range(kp, 0, -1):
        fk = f(k, u[k], +1)
        uk = u[k]

        def g(x):
            return x - uk + 0.5 * dt * (fk + f(k - 1, x, +1))
        lo = ub[k - 1] * (1 - 1e-15)
        if g(lo) > 0:
            u[k - 1] = lo
            nclip += 1
            continue
        hi = uk + 1e-30
        while g(hi) < 0:
            hi = hi * 1.5 + 1e-12
        u[k - 1] = brentq(g, lo, hi, xtol=1e-17 * max(uk, 1e-30), rtol=1e-15)
    for k in range(kp, n - 1):
        fk = f(k, u[k], ramo_depois)
        uk = u[k]

        def g(x):
            return x - uk - 0.5 * dt * (fk + f(k + 1, x, ramo_depois))
        lo = ub[k + 1] * (1 - 1e-15)
        if ramo_depois < 0:
            if g(lo) > 0:
                u[k + 1] = lo
                nclip += 1
                continue
            hi = max(uk, ub[k + 1]) * 1.0000001 + 1e-30
            while g(hi) < 0:
                hi = hi * 1.5 + 1e-12
        else:
            hi = max(uk, ub[k + 1]) * 2 + 1e-12
            while g(hi) < 0:
                hi *= 2
            if g(lo) > 0:
                u[k + 1] = lo
                nclip += 1
                continue
        u[k + 1] = brentq(g, lo, hi, xtol=1e-17 * max(uk, 1e-30), rtol=1e-15)
    return u, kp, nclip


# ------------------------------------------------------------------ metricas
def regioes(t, t_i, t_p=0.0):
    return {"inspiral (t_i+20, t_p-200)": (t > t_i + 20) & (t < t_p - 200),
            "fim da inspiral (t_p-200, t_p)": (t >= t_p - 200) & (t < t_p),
            "pos-pico (t_p, t_p+30)": (t >= t_p) & (t < t_p + 30),
            "toque (t_p+30, t_p+60)": (t >= t_p + 30) & (t < t_p + T_FIM)}


def regioes_exp09(t, tpk):
    """As duas regioes do exp09: inspiral = (t0+50, tpk-200), fusao = [tpk-200, tpk+30)."""
    return {"exp09 inspiral": (t < tpk - 200) & (t > t[0] + 50), "exp09 fusao": (t >= tpk - 200) & (t < tpk + 30)}


def erro_rel(x, ref, m):
    e = np.abs(x[m] / ref[m] - 1)
    return float(np.median(e)), float(np.max(e))


def fase_acumulada(psid, t, t_i, dt):
    """Fase int_{t_i}^t psidot (trapezio a partir do primeiro ponto >= t_i)."""
    k = int(np.searchsorted(t, t_i))
    out = np.full(len(t), np.nan)
    out[k:] = np.concatenate([[0.0], np.cumsum(0.5 * dt * (psid[k:-1] + psid[k + 1:]))])
    return out


def overlap_fase(a, b):
    """|<a, b>| / (|a||b|) maximizado so na fase constante (sem translacao no tempo)."""
    return float(np.abs(np.vdot(a, b)) / np.sqrt(np.vdot(a, a).real * np.vdot(b, b).real))


def gerar(q, c1, c2, M=65.0, f_ini=10.0, t_desloc=0.0, f0=None):
    """Onda na rede fixa (observaveis.gerar_janela); f0 adimensional opcional (como no exp09)."""
    if f0 is not None:
        f_ini = f0 / (M * MSUN_S)
    return O.gerar_janela(q, c1, c2, M, f_ini, t_desloc=t_desloc)
