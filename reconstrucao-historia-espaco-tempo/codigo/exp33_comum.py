"""Ferramentas comuns das linhas L10 (precessao, multipolos m != 0) e L11 (zeros da memoria no ceu).

Modelo: NRSur7dq4 (Varma et al. 2019, arXiv:1905.09300), substituto precessante de RN, modos l <= 4 no
referencial inercial, q <= 4 (treino; 6 com extrapolacao), |chi| <= 0.8, ~4300 M antes do pico.

Convencoes do gwsurrogate (lidas na docstring e no codigo de gwsurrogate/new/precessing_surrogate.py):
  - spins chiA (mais pesado), chiB dados na epoca de referencia, no referencial coorbital: z = L (eixo do
    referencial coprecessante), x = n (do mais leve para o mais pesado), y = z x x;
  - f_ref = 0: a epoca de referencia e o primeiro no da dinamica (t = -4300 M);
    f_ref = f0 > 0: t_ref em que a frequencia orbital coprecessante vale pi f0 (linear entre nos, com um
    passo de Euler ate o no mais proximo, ver _initialize);
  - o referencial inercial da saida coincide com o coorbital na epoca de referencia.

Nivel A (como observaveis.py): as memorias nulas sao calculadas pelos fluxos dos modos radiativos. O NRSur7dq4 foi
treinado em ondas extrapoladas do SXS, cujos modos m = 0 NAO contem a memoria (exp33_validacao, teste (g): o (2,0)
coorbital termina em ~5e-5, contra ~0.1 de memoria esperada); os seus modos coorbitais m = 0 sao radiacao ordinaria
(toque quase normal dos m = 0 e, em precessao, partes imaginarias de ~1e-2 que nao existem com spins alinhados).
Por isso o padrao e usar TODOS os modos (zerar_m0=False). A opcao zerar_m0=True zera os modos coorbitais m = 0 antes
da rotacao para o referencial inercial (variante "como o nivel A do CCE", que descarta os m = 0); com spins alinhados
equivale a descartar os modos inerciais (l, 0).

Nada de cache de formas de onda: as funcoes geram, calculam e devolvem numeros.
"""
import functools

import numpy as np

import observaveis as O
from memorias import CalculadoraMemoria
from harmonicos import sYlm, Dfrak, ethb2_de_escalar

MODOS = [(l, m) for l in range(2, 5) for m in range(-l, l + 1)]
MODOS_SEM_M0 = [k for k in MODOS if k[1] != 0]
TIPOS = O.TIPOS
LMAX_SAIDA = 8
F0_PADRAO = 0.007          # f_22 adimensional do inicio da janela (acima do inicio do NRSur7dq4 em q <= 4, |chi| <= 0.8)


@functools.lru_cache(maxsize=1)
def sur7():
    import gwsurrogate
    return gwsurrogate.LoadSurrogate("NRSur7dq4")


class _ZeraM0:
    """Envolve o substituto coorbital e zera as linhas m = 0 (ordem l = 2..ellMax, m = -l..l)."""

    def __init__(self, orig):
        self.orig = orig

    def __call__(self, q, chiA, chiB, ellMax=4):
        modos = self.orig(q, chiA, chiB, ellMax=ellMax)
        for l in range(2, ellMax + 1):
            modos[l * l - 4 + l] = 0.0
        return modos

    def __getattr__(self, nome):
        return getattr(self.orig, nome)


def gerar7(q, chiA, chiB, dt=0.25, f_ref=0.0, zerar_m0=False):
    """Onda NRSur7dq4 na rede fixa t_k = k dt (t = 0 no pico) e a dinamica.

    Devolve (t, h, dyn): h dict (l, m) -> array complexo (adimensional, r h / M); dyn com 'chiA', 'chiB' (inerciais,
    (N, 3)), 'q_copr' (4, N), 'orbphase' (N,).
    """
    s = sur7()
    ps = s._sur_dimless
    tc = ps.t_coorb
    tt = np.arange(int(np.ceil(tc[0] / dt)), int(np.floor(tc[-1] / dt)) + 1) * dt
    orig = ps.coorb_sur
    if zerar_m0:
        ps.coorb_sur = _ZeraM0(orig)
    try:
        t, h, dyn = s(float(q), [float(x) for x in chiA], [float(x) for x in chiB], times=tt, f_low=0,
                      f_ref=f_ref, precessing_opts={"return_dynamics": True})
    finally:
        ps.coorb_sur = orig
    h = {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}
    return np.asarray(t), h, dyn


def instante_orbital(t, orbphase, f0):
    """t_i em que a frequencia orbital coprecessante vale pi f0 (f_22 = f0), interpolacao linear; antes do pico."""
    w = O.derivada(np.asarray(orbphase)[:, None], t[1] - t[0], 8)[:, 0]
    w0 = np.pi * f0
    ate = np.nonzero(t <= 0)[0]
    acima = ate[w[ate] >= w0]
    if len(acima) == 0 or acima[0] < 8:
        raise ValueError("f0 fora do trecho gerado")
    k = int(acima[0])
    return float(t[k - 1] + (w0 - w[k - 1]) / (w[k] - w[k - 1]) * (t[k] - t[k - 1]))


@functools.lru_cache(maxsize=4)
def calculadora(modos):
    return CalculadoraMemoria(list(modos), lmax_saida=LMAX_SAIDA + 1)


def taxa_J(h, hd, modos):
    """Taxa de momento angular irradiado dJ/dt (vetor, unidades M) a partir dos modos (Ruiz et al. 2008, eqs. 3.22-3.24).

    dJx = (1/32pi) Im sum h_lm [f(l,m) conj(hd_l,m+1) + f(l,-m) conj(hd_l,m-1)]
    dJy = -(1/32pi) Re sum h_lm [f(l,m) conj(hd_l,m+1) - f(l,-m) conj(hd_l,m-1)]
    dJz = (1/16pi) Im sum m h_lm conj(hd_lm),   f(l,m) = sqrt((l-m)(l+m+1)).
    h, hd: dict ou arrays por modo (mesmo eixo de tempo). Sinais conferidos (exp33_validacao): Jz > 0 para orbita com
    L em +z, e J_rad ~ J_i - J_f.
    """
    def f(l, m):
        v = (l - m) * (l + m + 1)
        return np.sqrt(v) if v > 0 else 0.0
    jx = jy = jz = 0.0
    for (l, m) in modos:
        a = h[(l, m)]
        up = hd.get((l, m + 1), 0.0) if (l, m + 1) in hd else 0.0
        dn = hd.get((l, m - 1), 0.0) if (l, m - 1) in hd else 0.0
        jx = jx + np.imag(a * (f(l, m) * np.conj(up) + f(l, -m) * np.conj(dn))) / (32 * np.pi)
        jy = jy - np.real(a * (f(l, m) * np.conj(up) - f(l, -m) * np.conj(dn))) / (32 * np.pi)
        jz = jz + m * np.imag(a * np.conj(hd[(l, m)])) / (16 * np.pi)
    return jx, jy, jz


def memorias7(q, t, h, dyn, t_i, modos=MODOS, ordem_deriv=8, pesos=None):
    """Memorias globais acumuladas de t_i ao fim (nivel A, desl de janela), todos os (l, m), l <= 8.

    Devolve (mem, aux). mem[tipo][(l, m)] no formato de observaveis (nivel de deformacao; CM = nula + ordinaria
    -(3/2) M_f Dfrak^-1 Delta Phi com o deslocamento de janela). aux: E_janela, M_f (1 - E_janela - E_lig 3PN com
    chi . L em t_i), P_rad (vetor), J_rad (vetor), chiA_i, chiB_i (inerciais em t_i), Lhat_i (eixo coprecessante em
    t_i), Lhat_pico (eixo coprecessante no pico).
    """
    modos = tuple(modos)
    calc = calculadora(modos)
    dtt = t[1] - t[0]
    H = np.stack([h[k] for k in modos], axis=1)
    Hd = O.derivada(H, dtt, ordem_deriv)
    w = O.pesos_janela(t, t_i) if pesos is None else pesos
    m = calc.memorias_gram(*O.gram_pesos(H, Hd, w))
    hd = {k: Hd[:, j] for j, k in enumerate(modos)}
    jx, jy, jz = taxa_J(h, hd, modos)
    Jrad = np.array([np.sum(w * jx), np.sum(w * jy), np.sum(w * jz)])
    del H, Hd, hd
    E_jan = float(m["energia_total"])
    chiA_i = np.array([O._interp_em(t, dyn["chiA"][:, k], t_i) for k in range(3)])
    chiB_i = np.array([O._interp_em(t, dyn["chiB"][:, k], t_i) for k in range(3)])
    Li = eixo_copr(np.array([O._interp_em(t, dyn["q_copr"][k], t_i) for k in range(4)]))
    Lp = eixo_copr(np.array([O._interp_em(t, dyn["q_copr"][k], 0.0) for k in range(4)]))
    f0 = float(np.interp(t_i, t, O.derivada(np.asarray(dyn["orbphase"])[:, None], dtt, 8)[:, 0]) / np.pi)
    x_i = (np.pi * f0) ** (2 / 3)
    E_l = float(O.e_lig(x_i, q, float(chiA_i @ Li), float(chiB_i @ Li), 3))
    Mf = 1.0 - E_jan - E_l
    P = momento(m["energia_modos"])
    out = {}
    for tipo in TIPOS:
        out[tipo] = {k: complex(v) for k, v in m[tipo].items() if k[0] <= LMAX_SAIDA}
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dPhi = 2 * dJ / ethb2_de_escalar(l)
            dK = -1.5 * Mf * dPhi / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    aux = dict(E_janela=E_jan, E_lig=E_l, M_f=Mf, P_rad=P, J_rad=Jrad, chiA_i=chiA_i, chiB_i=chiB_i, Lhat_i=Li,
               Lhat_pico=Lp, x_i=x_i, t_i=float(t_i))
    return out, aux


def momento(E_modos):
    """Momento linear irradiado (vetor) pelos modos l = 1 de int |hdot|^2 (como binarias.momento_irradiado)."""
    c = np.sqrt(4 * np.pi / 3)
    Pz = c * E_modos[(1, 0)].real / (16 * np.pi)
    pxpy = -np.sqrt(2) * c * np.conj(E_modos[(1, 1)]) / (16 * np.pi)
    return np.array([pxpy.real, pxpy.imag, Pz])


def eixo_copr(qt):
    """Eixo z do referencial coprecessante (vetor unitario) a partir do quaternio (q0, qx, qy, qz): R(q) z."""
    a, b, c, d = np.asarray(qt) / np.linalg.norm(qt)
    return np.array([2 * (b * d + a * c), 2 * (c * d - a * b), a * a - b * b - c * c + d * d])


# ------------------------------------------------------------------ vetores reais e rotacoes
def vetor_real(mem, tipos=TIPOS, lmax=4, lmin=None):
    """Vetor real ortonormal dos multipolos: para cada tipo e l, a_l0 (parte real; imaginaria para spin) e
    sqrt(2) Re a_lm, sqrt(2) Im a_lm (m > 0). Assim sum v^2 = sum_m |a_lm|^2 = integral |campo|^2 no ceu.
    Devolve (v, rotulos)."""
    v, rot = [], []
    for tipo in tipos:
        l0 = (0 if tipo == "giroscopica" else 2) if lmin is None else lmin
        for l in range(l0, lmax + 1):
            a0 = mem[tipo].get((l, 0), 0j)
            v.append(a0.imag if tipo == "spin" else a0.real)
            rot.append((tipo, l, 0, "0"))
            for m in range(1, l + 1):
                a = mem[tipo].get((l, m), 0j)
                v += [np.sqrt(2) * a.real, np.sqrt(2) * a.imag]
                rot += [(tipo, l, m, "re"), (tipo, l, m, "im")]
    return np.array(v), rot


def girar_gerador(mem, eixo):
    """Derivada dos multipolos sob rotacao infinitesimal em torno de eixo ('x', 'y', 'z'): delta a = -i (L_k a).

    (L_z a)_lm = m a_lm ; (L_+ a)_lm = sqrt((l-m+1)(l+m)) a_l,m-1 ; (L_- a)_lm = sqrt((l+m+1)(l-m)) a_l,m+1.
    Vale para qualquer peso de spin (sYlm se transformam pelas matrizes D^l como os Ylm)."""
    out = {}
    for tipo in mem:
        d = mem[tipo]
        r = {}
        for (l, m), _ in d.items():
            am1 = d.get((l, m - 1), 0j)
            ap1 = d.get((l, m + 1), 0j)
            Lp = np.sqrt(max((l - m + 1) * (l + m), 0)) * am1
            Lm = np.sqrt(max((l + m + 1) * (l - m), 0)) * ap1
            if eixo == "z":
                La = m * d[(l, m)]
            elif eixo == "x":
                La = 0.5 * (Lp + Lm)
            else:
                La = (Lp - Lm) / 2j
            r[(l, m)] = -1j * La
        out[tipo] = r
    return out


def campo_ceu(mem_tipo, theta, phi, s=-2):
    """Soma sum a_lm sY_lm(theta, phi) (arrays)."""
    z = 0.0
    for (l, m), c in mem_tipo.items():
        if l >= abs(s) and c != 0:
            z = z + c * sYlm(s, l, m, theta, phi)
    return z
