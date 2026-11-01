"""Experimento 40 (linha L16): funcoes comuns para binarias excentricas (SEOBNRv5EHM, nivel A) com janelas fisicas.

Diferencas em relacao ao exp12 (todas opcionais, para comparar):
  - anomalia relativistica inicial l0 livre (rel_anomaly), como no rev_R4;
  - modo (2,0) OSCILATORIO newtoniano das orbitas excentricas (o modelo nao o tem), calculado da dinamica EOB
    (r(t), phi(t)) pela formula do quadrupolo, h_ij = 2 d^2(nu x_i x_j)/dt^2 projetado em (-2)Y_20 com os
    projetores de pn_excentrico; desligado por um cosseno entre t = -200 M e -100 M (antes do pico), onde a
    orbita ja circularizou e a formula newtoniana deixa de valer; entra nos fluxos como mais um modo;
  - energia de ligacao no inicio da janela pela propria Hamiltoniana EOB: E_lig = 1 - nu H(t_w) (coluna 8 da
    dinamica; confere com a E_lig 3PN+SO do observaveis a 5e-7 no caso circular e inclui a excentricidade);
    M_f = 1 - E_janela - E_lig(t_w);
  - derivada de 8a ordem e pesos de trapezio com inicio exato (observaveis.derivada, observaveis.pesos_janela);
  - segunda janela que comeca quando a frequencia orbital MEDIA atinge f2: media de phi entre passagens
    sucessivas pelo periastro (maximos de Omega na dinamica, refinados por parabola), atribuida ao instante medio
    e interpolada por spline cubica; no caso circular (e0 = 0) usa a frequencia instantanea.
A primeira janela comeca no inicio da onda (EccIC = 1: frequencia orbital media do modelo = pi M f_ini).
So os multipolos m = 0 (como no exp12). Nao guarda formas de onda: devolve so dicionarios pequenos.
"""
import logging
import os
import sys
import warnings

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import observaveis as O                                 # noqa: E402
from deteccao import MSUN_S                             # noqa: E402
from harmonicos import Dfrak, ethb2_de_escalar          # noqa: E402
from memorias import CalculadoraMemoria                 # noqa: E402

MODOS = [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3)]
LISTA = []
for (_l, _m) in MODOS:
    LISTA += [(_l, _m), (_l, -_m)]
RES = os.path.join(AQUI, "..", "resultados")
A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0), e=0.0, l0=0.0)
TIPOS = B.TIPOS
_calcs = {}
logging.getLogger("pyseobnr").setLevel(logging.ERROR)


def calc(com20):
    if com20 not in _calcs:
        _calcs[com20] = CalculadoraMemoria(LISTA + ([(2, 0)] if com20 else []))
    return _calcs[com20]


def gerar(q, c1, c2, M, e0, l0=0.0, f_ini=10.0):
    """t (M), modos (com m < 0), dinamica (colunas t, r, phi, pr, pphi, e, z, x, H/mu, Omega) e t_shift.

    Tempo da onda = tempo da dinamica - t_shift (t_shift = -t[0])."""
    from pyseobnr.generate_waveform import generate_modes_opt
    f0 = M * MSUN_S * f_ini
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        t, modos, model = generate_modes_opt(q, c1, c2, np.pi * f0, eccentricity=e0, rel_anomaly=l0,
                                             approximant="SEOBNRv5EHM", debug=True)
    h = {}
    for chave, v in modos.items():
        l, m = (int(x) for x in chave.split(","))
        h[(l, m)] = np.asarray(v)
        h[(l, -m)] = (-1) ** l * np.conj(h[(l, m)])
    t = np.asarray(t)
    dyn = np.array(model.dynamics)
    nu = float(model.nu)
    del model
    return t, h, dyn, nu, -float(t[0])


def h20_newton(t, dyn, nu, t_shift, corte=(-200.0, -100.0)):
    """Modo (2,0) oscilatorio newtoniano a partir de r(t), phi(t) da dinamica EOB, na grade t da onda."""
    from scipy.interpolate import CubicSpline
    import pn_excentrico as PN
    td = dyn[:, 0] - t_shift
    ok = (t >= td[0]) & (t <= td[-1])
    r = CubicSpline(td, dyn[:, 1])(t[ok])
    ph = CubicSpline(td, dyn[:, 2])(t[ok])
    dt = t[1] - t[0]
    x = np.stack([r * np.cos(ph), r * np.sin(ph), np.zeros_like(r)], axis=1)
    P = PN._projetores()[(2, 0)]
    # contracao direta: f(t) = sum_ij nu x_i x_j P_ij, depois segunda derivada
    f = nu * np.einsum("ti,tj,ij->t", x, x, P)
    d2 = np.gradient(np.gradient(f, dt, edge_order=2), dt, edge_order=2)
    d2[2:-2] = (-f[4:] + 16 * f[3:-1] - 30 * f[2:-2] + 16 * f[1:-3] - f[:-4]) / (12 * dt ** 2)
    out = np.zeros(len(t), dtype=complex)
    out[ok] = 2 * d2
    a, b = corte
    jan = np.where(t < a, 1.0, np.where(t > b, 0.0, 0.5 * (1 + np.cos(np.pi * (t - a) / (b - a)))))
    return out * jan


def instante_freq_media(dyn, t_shift, f_alvo, e0):
    """Instante (tempo da onda) em que a frequencia orbital media vale pi f_alvo (adimensional, = pi M f)."""
    from scipy.interpolate import CubicSpline
    td = dyn[:, 0]
    w_alvo = np.pi * f_alvo
    Om = dyn[:, 9]
    if e0 <= 0.0:
        k = int(np.nonzero(Om >= w_alvo)[0][0])
        return float(td[k - 1] + (w_alvo - Om[k - 1]) / (Om[k] - Om[k - 1]) * (td[k] - td[k - 1]) - t_shift)
    phs = CubicSpline(td, dyn[:, 2])
    j = np.nonzero((Om[1:-1] > Om[:-2]) & (Om[1:-1] >= Om[2:]))[0] + 1      # maximos de Omega (periastros)
    tp = []
    for i in j:
        y0, y1, y2 = Om[i - 1], Om[i], Om[i + 1]
        x0, x1, x2 = td[i - 1], td[i], td[i + 1]
        den = (x0 - x1) * (x0 - x2) * (x1 - x2)
        A_ = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
        B_ = (x2 ** 2 * (y0 - y1) + x1 ** 2 * (y2 - y0) + x0 ** 2 * (y1 - y2)) / den
        tp.append(-B_ / (2 * A_) if A_ < 0 else x1)
    tp = np.array(tp)
    wm = (phs(tp[1:]) - phs(tp[:-1])) / (tp[1:] - tp[:-1])
    tm = 0.5 * (tp[1:] + tp[:-1])
    sel = np.nonzero(wm >= w_alvo)[0]
    if len(sel) == 0 or sel[0] < 2:
        raise ValueError("frequencia media alvo fora do trecho")
    k = int(sel[0])
    s = slice(max(k - 4, 0), min(k + 4, len(wm)))
    cs = CubicSpline(tm[s], wm[s] - w_alvo)
    raizes = [r_ for r_ in cs.roots() if tm[k - 1] - 1e-9 <= r_ <= tm[k] + 1e-9]
    tr = float(raizes[0]) if raizes else float(tm[k - 1] + (w_alvo - wm[k - 1]) / (wm[k] - wm[k - 1]) * (tm[k] - tm[k - 1]))
    return tr - t_shift


def memorias(t, h, t_w, dyn, nu, t_shift, com20=False, h20=None, elig="eob", x0=None):
    """Memorias m = 0 (l <= 8) acumuladas de t_w ao fim, nivel A, e auxiliares.

    elig='eob': E_lig = 1 - nu H(t_w) (Hamiltoniana EOB, inclui a excentricidade); elig='pn1': formula 1PN
    circular do exp12, (nu x0/2)(1 - (3/4 + nu/12) x0), com x0 dado (so para comparar com o exp12)."""
    lista = LISTA + ([(2, 0)] if com20 else [])
    hh = dict(h)
    if com20:
        hh[(2, 0)] = h20
    H = np.stack([hh[k] for k in lista], axis=1)
    Hd = O.derivada(H, t[1] - t[0], 8)
    tw = max(t_w, t[0] + 1e-9)
    w = O.pesos_janela(t, tw)
    m = calc(com20).memorias_gram(*O.gram_pesos(H, Hd, w))
    del H, Hd
    out = B._mem_m0(m)
    E_jan = float(m["energia_total"])
    if elig == "eob":
        E_l = 1.0 - nu * float(np.interp(tw + t_shift, dyn[:, 0], dyn[:, 8]))
    else:
        E_l = 0.5 * nu * x0 * (1 - (0.75 + nu / 12) * x0)
    Mf = 1.0 - E_jan - E_l
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dK = -1.5 * Mf * (2 * dJ / ethb2_de_escalar(l)) / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    P = B.momento_irradiado(m["energia_modos"])
    return out, dict(M_f=Mf, E_janela=E_jan, E_lig=E_l, recuo=-P / Mf, t_w=tw)


def avaliar(q, c1, c2, M, e0, l0, freqs=(10.0, 20.0), com20=True, corte=(-200.0, -100.0), tambem_sem20=False,
            variantes=False):
    """Memorias m = 0 em cada janela (freqs em Hz de frequencia de onda media). Devolve lista de dicts e extras.

    Cada dict: 'com' = (mem, aux) com as opcoes pedidas (com20, E_lig EOB); se tambem_sem20, 'sem' = sem o (2,0)
    oscilatorio; se variantes (so na 1a janela), 'exp12' = sem (2,0) e com E_lig 1PN circular (cadeia do exp12,
    exceto derivada de 8a ordem) e 'so20' = com (2,0) e E_lig 1PN."""
    t, h, dyn, nu, ts_ = gerar(q, c1, c2, M, e0, l0, freqs[0])
    h20 = h20_newton(t, dyn, nu, ts_, corte) if (com20 or tambem_sem20 or variantes) else None
    res = []
    for k, f in enumerate(freqs):
        tw = t[0] if k == 0 else instante_freq_media(dyn, ts_, M * MSUN_S * f, e0)
        r = dict(com=memorias(t, h, tw, dyn, nu, ts_, com20, h20))
        if tambem_sem20:
            r["sem"] = memorias(t, h, tw, dyn, nu, ts_, False)
        if variantes and k == 0:
            x0 = (np.pi * M * MSUN_S * f) ** (2 / 3)
            r["exp12"] = memorias(t, h, tw, dyn, nu, ts_, False, elig="pn1", x0=x0)
            r["so20"] = memorias(t, h, tw, dyn, nu, ts_, True, h20, elig="pn1", x0=x0)
        res.append(r)
    extra = dict(max_h20_osc=float(np.max(np.abs(h20))) if h20 is not None else 0.0,
                 max_h22=float(np.max(np.abs(h[(2, 2)]))))
    del t, h, dyn
    return res, extra


def fisicos(mem, iota, M, D):
    return B.valores_fisicos(mem, iota, M, D)


def dif_rel(v, alvo):
    return {k: (v[k] - alvo[k]) / abs(alvo[k]) for k in TIPOS}
