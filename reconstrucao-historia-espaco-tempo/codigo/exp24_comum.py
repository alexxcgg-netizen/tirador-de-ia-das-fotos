"""Ferramentas comuns das linhas L05-L07 (agente D3): espectros da memoria nula e da onda, Fisher, match.

Usa observaveis.py (L00) para gerar a onda na rede fixa com t_i exato. Acrescenta:

1. Taxas instantaneas dos modos m = 0 de memoria (l = 2..8) por coeficientes angulares esparsos, obtidos UMA vez
   pela mesma quadratura de CalculadoraMemoria (pares (j,k) de modos oscilatorios com m_j = m_k):
       dmem_L(t) = fE_L sum_jk hdot_j conj(hdot_k) GE[j,k,L]                       (eletrica, l par)
       hB_L(t)   = fB_L Im{ sum_jk (3 hdot_j conj(h_k) - 3 h_j conj(hdot_k)) P1[j,k,L]
                             + (-conj(hdot_j) h_k + conj(h_j) hdot_k) P2[j,k,L] }   (magnetica, l impar)
   exatamente as formulas de memorias.partes_instantaneas restritas a m = 0 (conferido contra
   observaveis.serie_memoria em exp24_fisher_memoria.py, teste T1). Custo ~100 vezes menor.
2. Espectro EXATO de um degrau mantido para sempre: para uma serie s_k na rede t_k (passo DT) que comeca em zero
   (janela de Tukey ancorada em t_i) e termina num valor constante, com Delta s_k = s_k - s_{k-1} de suporte
   compacto,
       s~(F) = DT * A(F) / (1 - exp(-2 pi i F DT)),   A(F) = sum_k Delta s_k exp(-2 pi i F t_k)
   (t contado do pico, t = 0). Nao ha rampa nem valor mantido artificial (preparar/snr2 do L00 usam rampa).
   A derivada em F e exata: A'(F) = -2 pi i sum_k t_k Delta s_k exp(-2 pi i F t_k).
3. Lei de escala em M: s(t) = (M/D) S(t/M) => s~(f) = (M^2/D) S^(M f) e, com a forma adimensional fixa,
       d s~ / d ln M = (M^2/D) [2 S^(F) + F S^'(F)],   F = M f.
   (a dependencia da frequencia de inicio da janela, M f_ini, e conferida a parte: fora da banda.)
4. Resposta de um detector: s = F+ h+ + Fx hx = Re[exp(2 i psi) h] com |F| = 1 (detector otimo em psi = 0, o mesmo
   de snr2 do L00) e h = h+ - i hx.

Unidades: tempo adimensional (M) nas series; espectros fisicos em strain/Hz; PSD de deteccao.psd_serie.
"""
import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import binarias as B                                     # noqa: E402
import observaveis as O                                  # noqa: E402
from deteccao import MSUN_S, MPC_S, psd_serie            # noqa: E402
from harmonicos import sYlm, Dfrak, D2, ethb2_de_escalar, eth_fator   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
FIG = os.path.join(AQUI, "..", "figuras")
DT = 0.25
LS = list(range(2, 9))
PSDS = ("aLIGO", "A+", "ET", "CE")
FMIN = 10.0
SIST_A = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, D=400.0, iota=np.radians(50.0), psi=0.0)

# cores e estilo das figuras do projeto
COR = dict(azul="#2a78d6", laranja="#eb6834", verde="#1baf7a", texto="#52514e", fundo="#fcfcfb", grade="#e6e5e0")


def estilo(plt):
    plt.rcParams.update({"figure.facecolor": COR["fundo"], "axes.facecolor": COR["fundo"],
                         "axes.edgecolor": COR["texto"], "axes.labelcolor": COR["texto"],
                         "xtick.color": COR["texto"], "ytick.color": COR["texto"], "text.color": COR["texto"],
                         "axes.grid": True, "grid.color": COR["grade"], "font.size": 9})


# ------------------------------------------------------------------ coeficientes angulares (m = 0)
@functools.lru_cache(maxsize=1)
def tensores_m0():
    """Pares esparsos e coeficientes para dmem_L0 e hB_L0, L = 2..8, a partir da grade de CalculadoraMemoria."""
    c = B.calculadoras()[0]
    g = c.g
    Y, eY, ebY, w = c.Y, c.ethY, c.ethbY, c.w
    Y0 = np.array([g.Y(0, L, 0).ravel() for L in LS])
    Ym1 = np.array([g.Y(-1, L, 0).ravel() for L in LS])
    GE = np.einsum("jx,kx,Lx->jkL", Y, Y.conj(), Y0.conj() * w[None, :])
    P1 = np.einsum("jx,kx,Lx->jkL", Y, eY.conj(), Ym1.conj() * w[None, :])
    P2 = np.einsum("jx,kx,Lx->jkL", Y.conj(), ebY, Ym1.conj() * w[None, :])
    fE = np.array([0.5 * ethb2_de_escalar(L) * 0.25 / Dfrak(L) for L in LS])
    fB = np.array([-0.5j * ethb2_de_escalar(L) * 0.125 * eth_fator(-1, L) / (Dfrak(L) * D2(L)) for L in LS])
    out = {}
    for nome, T in (("E", GE), ("P1", P1), ("P2", P2)):
        mag = np.max(np.abs(T), axis=2)
        jj, kk = np.nonzero(mag > 1e-13 * np.max(mag))
        out[nome] = (jj, kk, T[jj, kk, :])
    return out, fE, fB


def taxas_m0(H, Hd, bloco=16384):
    """(dmem, hB): (n, 7) complexos, taxa da memoria nula eletrica e parte magnetica instantanea, L = 2..8, m = 0."""
    T, fE, fB = tensores_m0()
    n = H.shape[0]
    R = np.zeros((n, len(LS)), dtype=complex)
    HB = np.zeros_like(R)
    jE, kE, cE = T["E"]
    j1, k1, c1 = T["P1"]
    j2, k2, c2 = T["P2"]
    for i in range(0, n, bloco):
        h, hd = H[i:i + bloco], Hd[i:i + bloco]
        R[i:i + bloco] = (hd[:, jE] * np.conj(hd[:, kE])) @ cE
        W = ((3 * hd[:, j1] * np.conj(h[:, k1]) - 3 * h[:, j1] * np.conj(hd[:, k1])) @ c1
             + (-np.conj(hd[:, j2]) * h[:, k2] + np.conj(h[:, j2]) * hd[:, k2]) @ c2)
        HB[i:i + bloco] = np.imag(W)
    return R * fE[None, :], HB * fB[None, :]


def serie_modal(t, h, t_i, ordem_deriv=8):
    """Serie modal da memoria nula (eletrica acumulada desde t_i + magnetica instantanea), L = 2..8, m = 0.

    Mesma quadratura de observaveis.serie_memoria (subintervalo parcial [t_i, t_k]). Devolve (k, G): G[j] e o
    valor na rede em t[k + j], j >= 0 (t[k-1] < t_i <= t[k]); antes de t_i a serie e zero.
    """
    k = int(np.searchsorted(t, t_i, side="left"))
    dtt = t[1] - t[0]
    Losc = B.lista_osc()
    H = np.stack([h[kk] for kk in Losc], axis=1)[k - 1:]
    Hd = O.derivada(np.stack([h[kk] for kk in Losc], axis=1), dtt, ordem_deriv)[k - 1:]
    R, HB = taxas_m0(H, Hd)
    del H, Hd
    a = (t_i - t[k - 1]) / dtt
    L = t[k] - t_i
    n = R.shape[0]
    acum = np.zeros((n, len(LS)), dtype=complex)
    acum[1] = 0.5 * L * ((1 - a) * R[0] + (1 + a) * R[1])
    acum[2:] = acum[1] + np.cumsum(0.5 * dtt * (R[1:-1] + R[2:]), axis=0)
    return k, acum[1:] + HB[1:]


def taper(x, T):
    """Meia janela de Tukey: 0 para x <= 0, 1 para x >= T."""
    w = np.ones_like(x)
    w[x <= 0] = 0.0
    sel = (x > 0) & (x < T)
    w[sel] = 0.5 * (1 - np.cos(np.pi * x[sel] / T))
    return w


# ------------------------------------------------------------------ espectros (degrau mantido)
def espectro_degrau(tt, X, N, nmax):
    """Espectros adimensionais S^(F) e S^'(F) (F_n = n/(N DT), n < nmax) de canais reais X (n_t, n_c) na rede tt.

    X comeca em ~0 (janela) e termina constante; o valor final fica mantido para sempre. t contado do pico.
    """
    dX = np.diff(X, axis=0, prepend=np.zeros((1, X.shape[1])))
    F = np.arange(nmax) / (N * DT)
    fase = np.exp(-2j * np.pi * F * tt[0])[:, None]
    A = np.fft.rfft(dX, n=N, axis=0)[:nmax] * fase
    Ap = -2j * np.pi * np.fft.rfft(dX * tt[:, None], n=N, axis=0)[:nmax] * fase
    e = np.exp(-2j * np.pi * F * DT)[:, None]
    den = 1 - e
    den[0] = 1.0                             # F = 0 nao e usado (abaixo de f_min); zerado abaixo
    S = DT * A / den
    Sp = DT * (Ap / den - A * (2j * np.pi * DT * e) / den ** 2)
    S[0] = 0.0
    Sp[0] = 0.0
    return F, S, Sp


@functools.lru_cache(maxsize=4)
def _Ylist(iota, s=-2):
    return np.array([float(np.real(sYlm(s, L, 0, iota, 0.0))) for L in LS])


def dY_dcos(iota, eps=1e-6):
    """d Y_L0 / d cos(iota) por diferenca central em cos(iota)."""
    c = np.cos(iota)
    ip, im = np.arccos(min(c + eps, 1.0)), np.arccos(max(c - eps, -1.0))
    return (_Ylist(ip) - _Ylist(im)) / (np.cos(ip) - np.cos(im))


class EspectroMemoria:
    """Espectros adimensionais dos 14 canais da memoria nula (h+ e hx de cada L) de uma binaria intrinseca."""

    def __init__(self, q, c1, c2, M_ref, f_ini, N=2 ** 19, Fmax=0.5, T_tap=1500.0, t=None, h=None, t_i=None,
                 tipo="nula"):
        if h is None:
            t, h, t_i = O.gerar_janela(q, c1, c2, M_ref, f_ini)
        self.t_i = float(t_i)
        self.q, self.c1, self.c2 = q, c1, c2
        if tipo == "nula":
            k, G = serie_modal(t, h, t_i)
        elif tipo == "rn":
            k = int(np.searchsorted(t, t_i, side="left"))
            G = np.zeros((len(t) - k, len(LS)), dtype=complex)
            for j, L in enumerate((2, 3, 4)):
                v0 = O._interp_em(t, h[(L, 0)], t_i)
                G[:, j] = h[(L, 0)][k:] - v0
        else:
            raise ValueError(tipo)
        tt = t[k:]
        W = taper(tt - t_i, T_tap)
        Gw = G * W[:, None]
        X = np.concatenate([Gw.real, -Gw.imag], axis=1)      # canais h+ (Re) e hx (-Im) de cada L
        nmax = int(Fmax * N * DT) + 1
        if len(tt) > N:
            raise ValueError("N pequeno demais")
        self.F, S, Sp = espectro_degrau(tt, X, N, nmax)
        nL = len(LS)
        self.Sp_, self.Sx_ = S[:, :nL], S[:, nL:]
        self.Dp_, self.Dx_ = Sp[:, :nL], Sp[:, nL:]
        self.final = Gw[-1].copy()                            # valores finais (adimensionais) por L
        self.N = N

    def canais(self, iota):
        """(h+^(F), hx^(F)) adimensionais no angulo iota, e suas derivadas em F."""
        Y = _Ylist(iota)
        return self.Sp_ @ Y, self.Sx_ @ Y, self.Dp_ @ Y, self.Dx_ @ Y


def fisico(F, Sad, M, D_mpc):
    """Converte espectro adimensional para fisico: s~(f) = (M_s^2/D_s) S^(F), f = F/M_s."""
    Ms = M * MSUN_S
    return F / Ms, Sad * Ms * Ms / (D_mpc * MPC_S)


@functools.lru_cache(maxsize=16)
def psd_grade(nome, n, df, fmin=FMIN):
    """Pesos w = frac/S na grade f_n = n df: regra do ponto medio com o bin da borda f_min com peso fracionario
    frac = (f_n + df/2 - f_min)/df (sem o salto da soma de Riemann quando a grade muda)."""
    S = psd_serie(nome, n, df, max(fmin - 2 * df, 0.5 * fmin))
    f = np.arange(n) * df
    frac = np.clip((f + 0.5 * df - fmin) / df, 0.0, 1.0)
    w = np.where(np.isfinite(S), frac / S, 0.0)
    return w


def produto(a, b, w, df):
    """(a|b) = 4 Re sum a conj(b) / S df (w = 1/S, zero fora da banda)."""
    return 4.0 * df * float(np.real(np.sum(a * np.conj(b) * w)))


def matriz_produtos(D, w, df):
    """Gram (D_i | D_j) para uma lista de espectros."""
    Dm = np.array(D)
    G = 4.0 * df * np.real((Dm * w[None, :]) @ Dm.conj().T)
    return 0.5 * (G + G.T)


# ------------------------------------------------------------------ analise de Fisher
def analise_fisher(G, nomes, sig_prior, intrinsecos=None):
    """Autovalores branqueados pelo prior, d_ef, informacao mutua (bits), Cramer-Rao com e sem prior."""
    sp = np.array([sig_prior[n] for n in nomes])
    Gw = G * sp[:, None] * sp[None, :]
    lam, V = np.linalg.eigh(Gw)
    ordem = np.argsort(lam)[::-1]
    lam, V = lam[ordem], V[:, ordem]
    lam_c = np.clip(lam, 0, None)
    d_ef = float(np.sum(lam_c / (lam_c + 1)))
    mi = float(0.5 * np.sum(np.log2(1 + lam_c)))
    # Cramer-Rao sem prior (pseudo-inversa estavel pela escala do prior)
    try:
        C = np.linalg.inv(Gw)
        cr = np.sqrt(np.clip(np.diag(C), 0, None)) * sp
    except np.linalg.LinAlgError:
        cr = np.full(len(nomes), np.inf)
    Cpost_w = np.linalg.inv(Gw + np.eye(len(nomes)))
    post = np.sqrt(np.diag(Cpost_w)) * sp
    mi_par = 0.5 * np.log2(1.0 / np.diag(Cpost_w))        # bits por parametro (marginal)
    out = dict(lam=lam, V=V, d_ef=d_ef, mi=mi, cr=cr, post=post, mi_par=mi_par, cond=float(lam[0] / max(lam[-1], 1e-300)))
    if intrinsecos is not None:
        idx = [nomes.index(n) for n in intrinsecos]
        Ci = Cpost_w[np.ix_(idx, idx)]
        out["mi_intr"] = float(-0.5 * np.log2(np.linalg.det(Ci)))
    return out


SIG_PRIOR = dict(lnM=np.log(3.0) / np.sqrt(12), q=3.0 / np.sqrt(12), c1=1.6 / np.sqrt(12), c2=1.6 / np.sqrt(12),
                 lnD=np.log(5.0) / np.sqrt(12), cosi=2.0 / np.sqrt(12), t0=0.05, psi=np.pi / np.sqrt(12),
                 phi=2 * np.pi / np.sqrt(12), A=1.0)


# ------------------------------------------------------------------ match de memoria (amplitude e tempo livres)
def overlap_tempo(a, b, w, df, up=8):
    """O(tau) = (a | b(. - tau)) = Re sum_f c(f) exp(2 pi i f tau), c = 4 df a conj(b)/S, numa grade de atrasos.

    b(t - tau) tem espectro b~ exp(-2 pi i f tau). Grade circular de periodo 1/df, resolucao 1/(Nt df), Nt = 2(nf-1)up.
    """
    nf = len(a)
    c = a * np.conj(b) * w * 4 * df
    Nt = 2 * (nf - 1) * up
    full = np.zeros(Nt // 2 + 1, dtype=complex)
    full[:nf] = c
    serie = 0.5 * Nt * np.fft.irfft(full, n=Nt)
    tau = np.arange(Nt) / (Nt * df)
    tau[tau >= 0.5 / df] -= 1.0 / df
    return serie, tau


def match_memoria(a, b, w, df, f, up=8, refinar=True):
    """max_tau |(a|b(.-tau))| / sqrt((a|a)(b|b)) (amplitude livre com sinal, sem maximizar fase); e tau."""
    from scipy.optimize import minimize_scalar
    aa = produto(a, a, w, df)
    bb = produto(b, b, w, df)
    O_, tau = overlap_tempo(a, b, w, df, up=up)
    j = int(np.argmax(np.abs(O_)))
    t0 = tau[j]
    c = a * np.conj(b) * w * 4 * df
    sel = w > 0
    fs_, cs = f[sel], c[sel]

    def val(tt):
        return float(np.real(np.sum(cs * np.exp(2j * np.pi * fs_ * tt))))

    best = abs(val(t0))
    if refinar:
        h = 1.0 / (2 * (len(a) - 1) * up * df)
        r = minimize_scalar(lambda tt: -abs(val(tt)), bounds=(t0 - 2 * h, t0 + 2 * h), method="bounded",
                            options=dict(xatol=1e-10))
        if -r.fun > best:
            best, t0 = -r.fun, float(r.x)
    return best / np.sqrt(aa * bb), t0, aa, bb


# ------------------------------------------------------------------ sinal fisico numa grade arbitraria (interpolacao em F)
def splines(E, iota):
    """Splines cubicas (em F) de h+^ e hx^ adimensionais de E no angulo iota (para avaliar com qualquer M)."""
    from scipy.interpolate import CubicSpline
    hp, hx, _, _ = E.canais(iota)
    return CubicSpline(E.F, hp), CubicSpline(E.F, hx)


def sinal_memoria(sp, M, D_mpc, psi, f, t0=0.0):
    """s~(f) = (M_s^2/D_s) [cos 2psi h+^(M_s f) + sin 2psi hx^(M_s f)] exp(-2 pi i f t0), com sp = splines(E, iota)."""
    Ms = M * MSUN_S
    F = Ms * f
    if F.max() > sp[0].x[-1]:
        raise ValueError("grade fisica alem de Fmax do espectro (M f = %.3f > %.3f)" % (F.max(), sp[0].x[-1]))
    s = np.cos(2 * psi) * sp[0](F) + np.sin(2 * psi) * sp[1](F)
    return s * (Ms * Ms / (D_mpc * MPC_S)) * np.exp(-2j * np.pi * f * t0)


# ------------------------------------------------------------------ derivadas do sinal de memoria numa grade fisica qualquer
NOMES8 = ["lnM", "q", "c1", "c2", "lnD", "cosi", "t0", "psi"]


def derivadas_grade(par, f, passo=1e-3, f_ini=10.0, N=2 ** 19, Fmax=1.0, T_tap=1500.0, E0=None):
    """Sinal de memoria nula num detector (psi) e suas 8 derivadas na grade fisica f (interpolacao em F).

    par: dict q, c1, c2, M, D, iota, psi (t0 = 0). ln M pela lei de escala (S^ e S^'); q, chi1, chi2 por diferenca
    central de passo `passo` com M fixo; ln D, cos iota, t0, psi analiticos. Devolve (s, dict de derivadas).
    """
    from scipy.interpolate import CubicSpline
    M, D, iota, psi = par["M"], par["D"], par["iota"], par["psi"]
    Ms = M * MSUN_S
    k = Ms * Ms / (D * MPC_S)
    F = Ms * f
    if E0 is None:
        E0 = EspectroMemoria(par["q"], par["c1"], par["c2"], M, f_ini, N=N, Fmax=Fmax, T_tap=T_tap)
    Y, dY = _Ylist(iota), dY_dcos(iota)
    c2, s2 = np.cos(2 * psi), np.sin(2 * psi)

    def comb(E, Yv, deriv=False):
        if deriv:
            return c2 * (E.Dp_ @ Yv) + s2 * (E.Dx_ @ Yv)
        return c2 * (E.Sp_ @ Yv) + s2 * (E.Sx_ @ Yv)

    def em_f(E, Yv, deriv=False):
        if F.max() > E.F[-1]:
            raise ValueError("grade fisica alem de Fmax do espectro (M f = %.3f > %.3f)" % (F.max(), E.F[-1]))
        return CubicSpline(E.F, comb(E, Yv, deriv))(F)

    s = k * em_f(E0, Y)
    d = {"lnM": k * (2 * em_f(E0, Y) + F * em_f(E0, Y, True))}
    for nome in ("q", "c1", "c2"):
        vals = []
        for sgn in (-1, 1):
            p = dict(q=par["q"], c1=par["c1"], c2=par["c2"])
            p[nome] += sgn * passo
            E = EspectroMemoria(p["q"], p["c1"], p["c2"], M, f_ini, N=N, Fmax=Fmax, T_tap=T_tap)
            vals.append(k * em_f(E, Y))
            del E
        d[nome] = (vals[1] - vals[0]) / (2 * passo)
    d["lnD"] = -s
    d["cosi"] = k * em_f(E0, dY)
    d["t0"] = -2j * np.pi * f * s
    d["psi"] = k * CubicSpline(E0.F, -2 * s2 * (E0.Sp_ @ Y) + 2 * c2 * (E0.Sx_ @ Y))(F)
    return s, d
