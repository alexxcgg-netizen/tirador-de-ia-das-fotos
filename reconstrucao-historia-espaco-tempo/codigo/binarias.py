"""Memorias de binarias de buracos negros reais (relatividade geral), em tres niveis.

Modelo de onda: NRHybSur3dq8_CCE (Yoo et al. 2023, arXiv:2306.03148), substituto de
relatividade numerica com extracao caracteristica (CCE): contem a memoria completa da RG
nos modos m = 0 (2,0), (3,0), (4,0), alem dos oscilatorios (2,2), (2,1), (3,3), (3,2),
(4,4), (4,3), (5,5) e seus m < 0. Spins alinhados; q em [1, 8] (treino), |chi| <= 0.8.

Unidades adimensionais: tempo em M (massa total), h = r * (h_+ - i h_x) / M.

Janela: as memorias de spin, de CM e giroscopica acumulam desde o inicio da inspiral e
divergem quando a separacao inicial vai ao infinito (spin e giroscopica ~ x0^-1/2, ver
etapa 6). Por isso tudo e acumulado a partir de uma frequencia de onda fixa M f0 (padrao
0.004, isto e, x0 = (pi M f0)^(2/3) = 0.054, separacao ~ 18 M). A memoria de deslocamento
converge e e dada TOTAL (desde x = 0), com a parte anterior a janela tirada do substituto
(nivel C) ou da formula 3PN de Favata 2009 (nivel A).

Niveis (ver 07_binarias_reais.md):
  A    ordem quadratica: partes nulas pelas leis de balanco usando so os modos oscilatorios
       (m != 0); memoria de CM ordinaria = -(3/2) M_f Dfrak^-1 Delta Phi [Nichols2018,
       eq. KlmChargePhilm]; memoria de deslocamento antes da janela pela formula 3PN.
  B-NL as mesmas formulas, mas com os fluxos calculados com a deformacao completa (inclui os
       modos de memoria m = 0 dentro dos fluxos: termos cubicos).
  C    direto da deformacao completa de RN: deslocamento = h_l0 no fim; spin = int h_30 du;
       giroscopica = -Dfrak int Psi du (de h_30) + helicidade de todos os modos; CM =
       ordinaria com o deslocamento de RN + parte nula com todos os modos.
So os multipolos m = 0 sao comparados (os m != 0 sao termos de borda oscilatorios da janela).
"""
import functools

import numpy as np

from harmonicos import sYlm, Dfrak, D2, ethb2_de_escalar
from memorias import CalculadoraMemoria, gram

MODOS_OSC = [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3), (5, 5)]
MODOS_M0 = [(2, 0), (3, 0), (4, 0)]
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")


@functools.lru_cache(maxsize=1)
def _sur():
    import gwsurrogate
    return gwsurrogate.LoadSurrogate("NRHybSur3dq8_CCE")


def lista_osc():
    out = []
    for (l, m) in MODOS_OSC:
        out += [(l, m), (l, -m)]
    return out


@functools.lru_cache(maxsize=None)
def calculadoras():
    return CalculadoraMemoria(lista_osc()), CalculadoraMemoria(lista_osc() + MODOS_M0)


def derivada4(H, dt):
    """Derivada temporal por diferencas centrais de 4a ordem (2a ordem nas pontas)."""
    D = np.gradient(H, dt, axis=0, edge_order=2)
    D[2:-2] = (-H[4:] + 8 * H[3:-1] - 8 * H[1:-3] + H[:-4]) / (12 * dt)
    return D


def gerar(q, chi1, chi2, f0=0.004, dt=0.25):
    """t, dict de modos (todos, inclusive m = 0 e m < 0), adimensional."""
    t, h, _ = _sur()(q, [0, 0, chi1], [0, 0, chi2], dt=dt, f_low=f0)
    return t, {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}


def favata_h20(x, eta):
    """h_20 de memoria acumulada desde x = 0 ate x (Favata 2009, eq. H20, convencao de Kidder, alpha = +1)."""
    pi = np.pi
    s = (1 + x * (-4075 / 4032 + 67 / 48 * eta)
         + x ** 2 * (-151877213 / 67060224 - 123815 / 44352 * eta + 205 / 352 * eta ** 2)
         + pi * x ** 2.5 * (-253 / 336 + 253 / 84 * eta)
         + x ** 3 * (-4397711103307 / 532580106240
                     + (700464542023 / 13948526592 - 205 / 96 * pi ** 2) * eta
                     + 69527951 / 166053888 * eta ** 2 + 1321981 / 5930496 * eta ** 3))
    return 8 * np.sqrt(pi / 5) * eta * x * 5 / (14 * np.sqrt(6)) * s


def lrr_h40(x, eta):
    """h_40 de memoria (Blanchet LRR 2024, eq. Hmem, 1PN), mesma normalizacao e sinal de favata_h20."""
    return 8 * np.sqrt(np.pi / 5) * eta * x * (1 / (504 * np.sqrt(2))) * (
        1 + x * (-180101 / 29568 + 27227 / 1056 * eta))


def _mem_m0(m):
    """Extrai so os multipolos m = 0 (l <= 8) de um dicionario de memorias."""
    out = {}
    for tipo in TIPOS:
        out[tipo] = {k: v for k, v in m[tipo].items() if k[1] == 0 and k[0] <= 8}
    return out


def momento_irradiado(E_modos):
    """Momento linear irradiado a partir dos modos l = 1 de int |hdot|^2 (P = (1/16pi) int n |hdot|^2)."""
    c = np.sqrt(4 * np.pi / 3)
    Pz = c * E_modos[(1, 0)].real / (16 * np.pi)
    # n_x + i n_y = -sqrt(8 pi/3) Y_11 e E real => int (n_x + i n_y) E = -sqrt(8 pi/3) conj(E_11)
    pxpy = -np.sqrt(2) * c * np.conj(E_modos[(1, 1)]) / (16 * np.pi)
    return np.array([pxpy.real, pxpy.imag, Pz])


def memorias(q, chi1, chi2, f0=0.004, dt=0.25, nivel="A", t=None, h=None):
    """Memorias m = 0 (dicionarios por tipo) no nivel pedido, mais grandezas auxiliares."""
    if h is None:
        t, h = gerar(q, chi1, chi2, f0, dt)
    eta = q / (1 + q) ** 2
    x0 = (np.pi * f0) ** (2 / 3)
    c_osc, c_full = calculadoras()
    Losc = lista_osc()
    Hosc = np.stack([h[k] for k in Losc], axis=1)
    if nivel == "A":
        H, calc = Hosc, c_osc
    else:
        H = np.concatenate([Hosc, np.stack([h[k] for k in MODOS_M0], axis=1)], axis=1)
        calc = c_full
    Hd = derivada4(H, dt)
    m = calc.memorias_gram(*gram(H, Hd, dt))
    E_rad = m["energia_total"] + 0.5 * eta * x0 * (1 + x0 * (-0.75 - eta / 12))   # + antes da janela (1PN)
    Mf = 1.0 - E_rad
    P = momento_irradiado(m["energia_modos"])
    out = _mem_m0(m)
    # deslocamento total
    pre = {(2, 0): favata_h20(x0, eta), (4, 0): lrr_h40(x0, eta)}
    if nivel == "C":
        for l in (2, 4):
            out["deslocamento"][(l, 0)] = complex(h[(l, 0)][-1])
        # spin direto: int h_30 du (modo magnetico m = 0 de RN)
        S30 = np.sum(h[(3, 0)]) * dt
        out["spin"] = {k: (S30 if k == (3, 0) else 0j) for k in out["spin"]}
        spin_pot30 = 2j * S30 / ethb2_de_escalar(3)          # h^B = -(i/2) ethb^2 Psi
        out["giroscopica"][(3, 0)] = (-Dfrak(3) * spin_pot30 + 0.25 * m["helicidade_modos"][(3, 0)])
        for l in (5, 7):
            out["giroscopica"][(l, 0)] = 0.25 * m["helicidade_modos"][(l, 0)]
    else:
        for l in (2, 4):
            out["deslocamento"][(l, 0)] = out["deslocamento"][(l, 0)] + pre[(l, 0)]
    # CM: parte nula (ja em out["cm"]) + ordinaria -(3/2) M_f Dfrak^-1 Delta Phi, Delta Phi_l0 = 2 Delta J_l0 / ethb2(l)
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dPhi = 2 * dJ / ethb2_de_escalar(l)
            dK = -1.5 * Mf * dPhi / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    aux = dict(E_rad=E_rad, M_f=Mf, P_rad=P, v_recuo=-P / Mf, t=t, eta=eta, x0=x0)
    return out, aux


def vetor(mem, chaves=None):
    """Vetor real com os multipolos dominantes (parte real ou imaginaria conforme a paridade)."""
    if chaves is None:
        chaves = [("deslocamento", (2, 0)), ("deslocamento", (4, 0)), ("spin", (3, 0)), ("cm", (2, 0)),
                  ("cm", (4, 0)), ("giroscopica", (1, 0)), ("giroscopica", (3, 0))]
    v = []
    for tipo, k in chaves:
        z = mem[tipo].get(k, 0j)
        v.append(z.imag if tipo == "spin" else z.real)
    return np.array(v), chaves


def no_observador(mem, iota):
    """Valor das quatro memorias numa direcao (iota, qualquer phi: so m = 0), adimensional.

    deslocamento: r Delta h_+ / M ; spin: r int h_x du / M^2 ; CM: r int h_+ du / M^2 ;
    giroscopica: r^2 Phi / M^2. (Base de polarizacao alinhada com o eixo orbital projetado.)
    """
    vals = {}
    for tipo in TIPOS:
        s = 0 if tipo == "giroscopica" else -2
        z = sum(c * sYlm(s, l, m, iota, 0.0) for (l, m), c in mem[tipo].items())
        vals[tipo] = float(-np.imag(z)) if tipo == "spin" else float(np.real(z))
    return vals


def memorias_fisicas(q, chi1, chi2, M_msun, f_fis, nivel="A", dt=0.25):
    """Memorias com a janela comecando numa frequencia de onda fisica f_fis (Hz) no referencial do detector."""
    from deteccao import MSUN_S
    f0 = M_msun * MSUN_S * f_fis
    t, h = gerar(q, chi1, chi2, f0=f0, dt=dt)
    mem, aux = memorias(q, chi1, chi2, f0=f0, dt=dt, nivel=nivel, t=t, h=h)
    return mem, aux, t, h


def valores_fisicos(mem, iota, M_msun, D_mpc):
    """As quatro memorias no observador em unidades fisicas.

    deslocamento: Delta h_+ (adimensional); spin e CM: int h du (segundos); giroscopica: angulo (rad).
    """
    from deteccao import MSUN_S, MPC_S
    M, D = M_msun * MSUN_S, D_mpc * MPC_S
    v = no_observador(mem, iota)
    return {"deslocamento": v["deslocamento"] * M / D, "spin": v["spin"] * M * M / D,
            "cm": v["cm"] * M * M / D, "giroscopica": v["giroscopica"] * (M / D) ** 2}
