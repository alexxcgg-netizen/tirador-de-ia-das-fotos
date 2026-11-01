"""Comum das linhas L03/L04 (agente D2): memorias em varias janelas a partir de UMA forma de onda.

Para cada frequencia de inicio f_k (Hz, frequencia do modo (2,2) no detector) a janela e [t_i(f_k), fim]. A onda
e gerada uma vez desde min(f_k) (observaveis.gerar_janela) e cada janela usa o instante exato t_i(f_k)
(observaveis.instante_frequencia) e os pesos de observaveis.pesos_janela. O pos-processamento (deslocamento de
janela, CM com o mesmo deslocamento, M_f = 1 - E_janela - E_lig(x_i)) e copiado de
observaveis.memorias_observaveis linha a linha; conferido em exp20_teste_comum (diferenca ~1e-16).

Como todas as memorias sao lineares nas matrizes de Gram (B, A), a memoria de uma banda [f_a, f_b] e
m(f_a) - m(f_b) (a parte ordinaria da CM usa M_f, igual em todas as janelas a ~1e-5: ver aux['M_f']).

Nada de formas de onda em cache: as funcoes devolvem so numeros (ou, a pedido, a onda para uso imediato).
"""
import numpy as np

import binarias as B
import observaveis as O
from deteccao import MSUN_S, MPC_S
from harmonicos import Dfrak, ethb2_de_escalar

TIPOS = O.TIPOS
PAR_A = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, D=400.0, iota=float(np.radians(50.0)), phi=0.0)
NOMES = ("q", "c1", "c2", "M", "iota", "D", "phi")


def _pos(m, h, t, ti, f0, q, chi1, chi2, nivel, desl, todos_m, ordem_elig, w):
    """Pos-processamento identico ao de observaveis.memorias_observaveis."""
    x_i = (np.pi * f0) ** (2 / 3)
    eta = q / (1 + q) ** 2
    E_jan = float(m["energia_total"])
    E_l = float(O.e_lig(x_i, q, chi1, chi2, ordem_elig))
    Mf = 1.0 - E_jan - E_l
    P = B.momento_irradiado(m["energia_modos"])
    out = O._restringir(m, todos_m)
    if nivel == "C":
        for l in (2, 4):
            fim = complex(h[(l, 0)][-1])
            out["deslocamento"][(l, 0)] = fim if desl == "total" else fim - complex(O._interp_em(t, h[(l, 0)], ti))
        S30 = complex(np.sum(w * h[(3, 0)]))
        for k in out["spin"]:
            if k[1] == 0:
                out["spin"][k] = S30 if k == (3, 0) else 0j
        spin_pot30 = 2j * S30 / ethb2_de_escalar(3)
        out["giroscopica"][(3, 0)] = complex(-Dfrak(3) * spin_pot30 + 0.25 * m["helicidade_modos"][(3, 0)])
        for l in (5, 7):
            out["giroscopica"][(l, 0)] = complex(0.25 * m["helicidade_modos"][(l, 0)])
    elif desl == "total":
        out["deslocamento"][(2, 0)] += B.favata_h20(x_i, eta)
        out["deslocamento"][(4, 0)] += B.lrr_h40(x_i, eta)
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dPhi = 2 * dJ / ethb2_de_escalar(l)
            dK = -1.5 * Mf * dPhi / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    aux = dict(E_janela=E_jan, E_lig=E_l, M_f=Mf, P_rad=P, t_i=float(ti), x_i=x_i, eta=eta, f0=f0)
    return out, aux


def janelas(q, chi1, chi2, M, freqs, nivel="A", desl="janela", todos_m=False, dt=0.25, ordem_elig=3,
            devolver_onda=False):
    """Memorias (dict por tipo e (l, m)) para cada janela [t_i(f), fim], f em freqs (Hz). Uma so onda.

    Devolve lista de (mem, aux) na ordem de freqs; com devolver_onda=True devolve tambem (t, h).
    """
    freqs = [float(f) for f in freqs]
    fmin = min(freqs)
    t, h, ti0 = O.gerar_janela(q, chi1, chi2, M, fmin, dt)
    dtt = t[1] - t[0]
    c_osc, c_full = B.calculadoras()
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    if nivel == "A":
        calc = c_osc
    else:
        H = np.concatenate([H, np.stack([h[k] for k in B.MODOS_M0], axis=1)], axis=1)
        calc = c_full
    Hd = O.derivada(H, dtt, 8)
    res = []
    for f in freqs:
        f0 = M * MSUN_S * f
        ti = ti0 if f == fmin else O.instante_frequencia(t, h[(2, 2)], f0)[0]
        w = O.pesos_janela(t, ti)
        m = calc.memorias_gram(*O.gram_pesos(H, Hd, w))
        res.append(_pos(m, h, t, ti, f0, q, chi1, chi2, nivel, desl, todos_m, ordem_elig, w))
    del H, Hd
    if devolver_onda:
        return res, (t, h)
    del t, h
    return res


def no_obs(mem, iota, phi, M, D):
    """As quatro memorias fisicas no observador (vetor na ordem TIPOS)."""
    v = O.valores_fisicos_completo(mem, iota, phi, M, D)
    return np.array([v[k] for k in TIPOS])


def observaveis_K(par, freqs, todos_m=False, nivel="A", tipos=TIPOS, bandas=False):
    """Matriz (K, len(tipos)) das memorias fisicas no observador para as janelas desde freqs.

    bandas=True: devolve as memorias de banda [f_k, f_{k+1}] (k < K-1) e a ultima janela [f_K, fim].
    """
    res = janelas(par["q"], par["c1"], par["c2"], par["M"], freqs, nivel=nivel, todos_m=todos_m)
    idx = [TIPOS.index(t) for t in tipos]
    Y = np.array([no_obs(m, par["iota"], par.get("phi", 0.0), par["M"], par["D"])[idx] for m, _ in res])
    if bandas:
        Y = np.concatenate([Y[:-1] - Y[1:], Y[-1:]], axis=0)
    return Y


def escalas_padrao(par):
    """Escalas das colunas dos jacobianos (as da revisao R4): 0.1 em q, chi1, chi2; 1 Msol; 0.01 rad; 0.01 D; 0.01 rad."""
    return dict(q=0.1, c1=0.1, c2=0.1, M=1.0, iota=0.01, D=0.01 * par["D"], phi=0.01)


def jacobiano(par, freqs, nomes=("q", "c1", "c2", "M", "iota", "D"), todos_m=False, nivel="A", tipos=TIPOS,
              passos=None, ordem=4, bandas=False):
    """Jacobiano de ln|y| (y = memorias fisicas por janela e tipo, achatadas) em relacao aos parametros.

    Derivadas por diferencas centrais de 4a ordem (5 pontos) para q, chi1, chi2, M (regera a onda) e analiticas
    por diferencas da mesma onda para iota, phi, D (sem regerar). Passos padrao: 2e-3 em q, chi (piso de ruido
    do substituto ~3e-10, verificacao L00) e 5e-4 relativo em M (abaixo do periodo de 0,73% das oscilacoes
    com todos os m). Devolve (J, y0) com J[i, j] = d ln|y_i| / d theta_j (sem escala de colunas) e y0 = valores
    BRUTOS y_i (nao o logaritmo).
    """
    if passos is None:
        passos = dict(q=2e-3, c1=2e-3, c2=2e-3, M=5e-4 * par["M"], iota=1e-4, D=1e-3 * par["D"], phi=1e-4)
    res0 = janelas(par["q"], par["c1"], par["c2"], par["M"], freqs, nivel=nivel, todos_m=todos_m)
    idx = [TIPOS.index(t) for t in tipos]

    def _Y(p, res):
        Y = np.array([no_obs(m, p["iota"], p.get("phi", 0.0), p["M"], p["D"])[idx] for m, _ in res])
        if bandas:
            Y = np.concatenate([Y[:-1] - Y[1:], Y[-1:]], axis=0)
        return Y.ravel()

    y0 = _Y(par, res0)
    cols = []
    for n in nomes:
        hstep = passos[n]
        if ordem == 4:
            pts, pes = (-2, -1, 1, 2), (1 / 12, -8 / 12, 8 / 12, -1 / 12)
        else:
            pts, pes = (-1, 1), (-0.5, 0.5)
        if n in ("iota", "D", "phi"):
            # sem regerar a onda
            d = np.zeros_like(y0)
            for k, c in zip(pts, pes):
                p = dict(par)
                p[n] = par[n] + k * hstep
                d += c * np.log(np.abs(_Y(p, res0)))
            cols.append(d / hstep)
            continue
        d = np.zeros_like(y0)
        for k, c in zip(pts, pes):
            p = dict(par)
            p[n] = par[n] + k * hstep
            d += c * np.log(np.abs(observaveis_K(p, freqs, todos_m, nivel, tipos, bandas).ravel()))
        cols.append(d / hstep)
    return np.array(cols).T, y0


def svd_escalado(J, par, nomes, escalas=None):
    """Valores singulares do jacobiano com as colunas multiplicadas pelas escalas (padrao: escalas_padrao)."""
    esc = escalas or escalas_padrao(par)
    S = np.array([esc[n] for n in nomes])
    U, s, Vt = np.linalg.svd(J * S[None, :], full_matrices=False)
    return s, Vt


def freqs_geom(f1, f2, K):
    """K frequencias geometricamente espacadas de f1 a f2 (K = 1: so f1)."""
    if K == 1:
        return [float(f1)]
    return [float(f1 * (f2 / f1) ** (k / (K - 1))) for k in range(K)]
