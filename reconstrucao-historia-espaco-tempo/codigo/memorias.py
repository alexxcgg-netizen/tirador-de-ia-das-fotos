"""As quatro memorias gravitacionais (partes nulas) a partir dos modos h_lm(u).

Unidades: G = c = 1, h = r * (h_+ - i h_x), modos em (-2)Y_lm.

Fontes das formulas (lidas no LaTeX original dos artigos):
  - deslocamento: Mitman et al. 2020, eq. (ememoryfinal)
        Delta J^E = (1/2) ethb^2 Dfrak^-1 [ Delta m + (1/4) int |hdot|^2 du ]
  - spin e centro de massa: balanco do momento angular, Mitman et al. 2020,
    eqs. (bondiangmomevo_null) e (radiatedangmom). Com
        W = 3 hdot ethb(hbar) - 3 h ethb(hdotbar) - hdotbar ethb(h) + hbar ethb(hdot)
    (W = 64 pi qbar^A Jdot_A, peso de spin -1) vale, para l >= 2,
        Dfrak D^2 int Psi du  = Delta Im[eth qbar.Nhat] + (1/8) Im[eth int W du]   (spin)
        Dfrak D^2 Delta K     = Delta Re[eth qbar.Nhat] + (1/8) Re[eth int W du]   (CM)
    onde Psi e o potencial magnetico de C_AB e Delta K e o observavel de memoria de
    CM de Nichols 2018, eq. (DeltaCalK). As partes "ordinarias" (Delta Nhat) sao
    variacoes de cargas entre os estados inicial e final e ficam de fora aqui.
  - giroscopica: Seraj & Oblak 2022, eqs. (t12) e (s15):
        r^2 Phi = int du [ (1/4) D_a D_b Ctil^ab - (1/8) N_ab Ctil^ab ],
        Ctil_ab = eps_ca C_b^c.
    Com eps_(theta phi) = +sin(theta), Ctil corresponde a htil = -i h, e
        r^2 Phi = - Dfrak int Psi du + (1/4) int Im(hbar hdot) du.

A funcao `memorias_gram` usa so as duas matrizes de Gram
    B_jk = int hdot_j conj(hdot_k) du,     A_jk = int h_j conj(hdot_k) du,
e a funcao `memorias_tempo` calcula tudo de novo direto no tempo e na grade.
As duas tem de concordar; o fato de que tudo depende so de (B, A - A^dagger) e o
resultado central da etapa 3.
"""
import numpy as np

from harmonicos import (Grade, modos, eth_fator, ethb_fator, Dfrak, D2,
                        ethb2_de_escalar)


def derivada(H, dt, metodo="fft"):
    """Derivada temporal ao longo do eixo 0. 'fft' supoe sinal periodico (janela com folga)."""
    if metodo == "fft":
        n = H.shape[0]
        w = 2 * np.pi * np.fft.fftfreq(n, d=dt)
        F = np.fft.fft(H, axis=0)
        return np.fft.ifft(1j * w[:, None] * F if F.ndim == 2 else 1j * w * F, axis=0)
    return np.gradient(H, dt, axis=0, edge_order=2)


def _parte_real_escalar(coef, lista):
    """Modos de Re(f) para f escalar (spin 0): (f_lm + (-1)^m conj(f_l,-m))/2."""
    idx = {lm: k for k, lm in enumerate(lista)}
    out = np.zeros_like(coef)
    for k, (l, m) in enumerate(lista):
        out[..., k] = 0.5 * (coef[..., k] + (-1) ** m * np.conj(coef[..., idx[(l, -m)]]))
    return out


def _parte_imag_escalar(coef, lista):
    idx = {lm: k for k, lm in enumerate(lista)}
    out = np.zeros_like(coef)
    for k, (l, m) in enumerate(lista):
        out[..., k] = (coef[..., k] - (-1) ** m * np.conj(coef[..., idx[(l, -m)]])) / 2j
    return out


class CalculadoraMemoria:
    """Prepara a grade e os campos angulares para um conjunto de modos de entrada."""

    def __init__(self, lista_entrada, lmax_saida=None, ntheta=None, nphi=None):
        self.L = list(lista_entrada)
        lmax_in = max(l for l, _ in self.L)
        self.lmax = lmax_saida or 2 * lmax_in + 1
        ntheta = ntheta or (self.lmax + lmax_in + 6)
        nphi = nphi or (2 * (self.lmax + 2 * lmax_in) + 8)
        self.g = Grade(ntheta, nphi)
        g = self.g
        # campos angulares de cada modo de entrada (achatados na grade)
        self.Y = np.array([g.Y(-2, l, m).ravel() for (l, m) in self.L])
        self.ethY = np.array([eth_fator(-2, l) * g.Y(-1, l, m).ravel() for (l, m) in self.L])
        self.ethbY = np.array([ethb_fator(-2, l) * g.Y(-3, l, m).ravel() for (l, m) in self.L])
        self.w = g.peso.ravel()
        self.lista0 = modos(self.lmax, 0)      # saidas escalares
        self.lista1 = modos(self.lmax, 1)      # saidas de spin -1
        self.Y0 = g.matriz_Y(0, self.lista0)
        self.Ym1 = g.matriz_Y(-1, self.lista1)

    # ---------- projecoes ----------
    def _proj0(self, f):
        return (f * self.w) @ self.Y0.conj().T

    def _projm1(self, f):
        return (f * self.w) @ self.Ym1.conj().T

    # ---------- a partir dos campos integrados no tempo ----------
    def _montar(self, E, Z, Hel):
        """E = int|hdot|^2, Z = int W, Hel = int Im(hbar hdot): campos achatados na grade."""
        L0 = self.lista0
        E_lm = self._proj0(E)
        # deslocamento (parte nula): Delta J^E_lm = E_lm / sqrt((l+2)!/(l-2)!)
        desl = {}
        potE = {}
        for k, (l, m) in enumerate(L0):
            if l >= 2:
                desl[(l, m)] = 0.5 * ethb2_de_escalar(l) * (0.25 * E_lm[k]) / Dfrak(l)
                potE[(l, m)] = 0.25 * E_lm[k] / Dfrak(l)
        # eth Z (spin 0): (eth Z)_lm = sqrt(l(l+1)) Z_lm
        Z_lm = self._projm1(Z)
        ethZ = np.zeros(len(L0), dtype=complex)
        idx0 = {lm: k for k, lm in enumerate(L0)}
        for k, (l, m) in enumerate(self.lista1):
            ethZ[idx0[(l, m)]] = eth_fator(-1, l) * Z_lm[k]
        ImZ = _parte_imag_escalar(ethZ, L0)
        ReZ = _parte_real_escalar(ethZ, L0)
        spin_pot, cm_pot, spin_h, cm_h = {}, {}, {}, {}
        for k, (l, m) in enumerate(L0):
            if l >= 2:
                den = Dfrak(l) * D2(l)
                spin_pot[(l, m)] = 0.125 * ImZ[k] / den
                cm_pot[(l, m)] = 0.125 * ReZ[k] / den
                # nivel de deformacao (modos de int h du em (-2)Y_lm)
                spin_h[(l, m)] = -0.5j * ethb2_de_escalar(l) * spin_pot[(l, m)]
                cm_h[(l, m)] = 0.5 * ethb2_de_escalar(l) * cm_pot[(l, m)]
        Hel_lm = self._proj0(Hel)
        giro = {}
        for k, (l, m) in enumerate(L0):
            termo_spin = -Dfrak(l) * spin_pot[(l, m)] if l >= 2 else 0.0
            giro[(l, m)] = termo_spin + 0.25 * Hel_lm[k]
        # momento angular irradiado (parte l = 1 do balanco), para conferencia
        return dict(deslocamento=desl, potencial_E=potE, spin=spin_h, spin_potencial=spin_pot,
                    cm=cm_h, cm_potencial=cm_pot, giroscopica=giro,
                    energia_modos=dict(zip(L0, E_lm)), helicidade_modos=dict(zip(L0, Hel_lm)),
                    Z_modos=dict(zip(self.lista1, Z_lm)),
                    energia_total=float(np.real(np.sum(E * self.w))) / (16 * np.pi))

    def campos_gram(self, B, A):
        """Campos angulares integrados a partir das matrizes de Gram."""
        Y, eY, ebY = self.Y, self.ethY, self.ethbY
        E = np.real(np.einsum('jk,jx,kx->x', B, Y, Y.conj()))
        Om = A.conj().T - A                                   # A^dagger - A
        Z = (np.einsum('jk,jx,kx->x', Om, Y, 3 * eY.conj())
             + np.einsum('jk,kx,jx->x', Om, Y.conj(), ebY))
        Hel = np.real(np.einsum('jk,jx,kx->x', Om, Y, Y.conj()) / 2j)
        return E, Z, Hel

    def memorias_gram(self, B, A):
        return self._montar(*self.campos_gram(B, A))

    def memorias_tempo(self, H, Hd, dt, bloco=2048):
        """Calculo direto: campos h, hdot na grade, produtos e integral no tempo."""
        nx = self.Y.shape[1]
        E = np.zeros(nx)
        Z = np.zeros(nx, dtype=complex)
        Hel = np.zeros(nx)
        for i in range(0, H.shape[0], bloco):
            h = H[i:i + bloco] @ self.Y
            hd = Hd[i:i + bloco] @ self.Y
            eh = H[i:i + bloco] @ self.ethY          # eth h (spin -1)
            ehd = Hd[i:i + bloco] @ self.ethY
            ebh = H[i:i + bloco] @ self.ethbY        # ethb h (spin -3)
            ebhd = Hd[i:i + bloco] @ self.ethbY
            # ethb(hbar) = conj(eth h)
            W = (3 * hd * np.conj(eh) - 3 * h * np.conj(ehd)
                 - np.conj(hd) * ebh + np.conj(h) * ebhd)
            E += np.sum(np.abs(hd) ** 2, axis=0) * dt
            Z += np.sum(W, axis=0) * dt
            Hel += np.sum(np.imag(np.conj(h) * hd), axis=0) * dt
        return self._montar(E, Z, Hel)

    # ---------- partes nao lineares instantaneas da deformacao ----------
    def partes_instantaneas(self, H, Hd, lista_saida):
        """h^B(u) e h^E_CM(u) instantaneos do termo de fluxo, e taxa de memoria nula.

        Retorna arrays (Nt, len(lista_saida)) em (-2)Y_lm:
          hB  : parte magnetica gerada pelo fluxo de momento angular (modo de memoria de spin)
          hEJ : parte eletrica correspondente (nao e memoria; aparece no balanco de CM)
          dmem: d/du da memoria nula de deslocamento.
        """
        idx0 = {lm: k for k, lm in enumerate(self.lista0)}
        h = H @ self.Y
        hd = Hd @ self.Y
        eh = H @ self.ethY
        ehd = Hd @ self.ethY
        ebh = H @ self.ethbY
        ebhd = Hd @ self.ethbY
        W = (3 * hd * np.conj(eh) - 3 * h * np.conj(ehd) - np.conj(hd) * ebh + np.conj(h) * ebhd)
        E = np.abs(hd) ** 2
        E_lm = self._proj0(E)
        W_lm = self._projm1(W)
        ethW = np.zeros((H.shape[0], len(self.lista0)), dtype=complex)
        for k, (l, m) in enumerate(self.lista1):
            ethW[:, idx0[(l, m)]] = eth_fator(-1, l) * W_lm[:, k]
        ImW = _parte_imag_escalar(ethW, self.lista0)
        ReW = _parte_real_escalar(ethW, self.lista0)
        hB = np.zeros((H.shape[0], len(lista_saida)), dtype=complex)
        hEJ = np.zeros_like(hB)
        dmem = np.zeros_like(hB)
        for j, (l, m) in enumerate(lista_saida):
            k = idx0[(l, m)]
            den = Dfrak(l) * D2(l)
            hB[:, j] = -0.5j * ethb2_de_escalar(l) * 0.125 * ImW[:, k] / den
            hEJ[:, j] = 0.5 * ethb2_de_escalar(l) * 0.125 * ReW[:, k] / den
            dmem[:, j] = 0.5 * ethb2_de_escalar(l) * 0.25 * E_lm[:, k] / Dfrak(l)
        return hB, hEJ, dmem


def gram(H, Hd, dt):
    """Matrizes de Gram B = int hdot hdot^dagger du, A = int h hdot^dagger du."""
    B = (Hd.T @ Hd.conj()) * dt
    A = (H.T @ Hd.conj()) * dt
    return B, A


def momentos_espectrais(H, dt):
    """M1 = int w h~ h~^dag dw/2pi, M2 = int w^2 h~ h~^dag dw/2pi (convencao h~ = int h e^{iwu} du)."""
    n = H.shape[0]
    Ht = np.fft.ifft(H, axis=0) * n * dt          # aproxima int h e^{+iwu} du
    w = 2 * np.pi * np.fft.fftfreq(n, d=dt)
    dw = 2 * np.pi / (n * dt)
    M1 = (Ht.T * w) @ Ht.conj() * dw / (2 * np.pi)
    M2 = (Ht.T * w ** 2) @ Ht.conj() * dw / (2 * np.pi)
    return M1, M2


def diferenca_relativa(m1, m2, chaves=("deslocamento", "spin", "cm", "giroscopica")):
    """max |m1 - m2| / max |m1| para cada tipo de memoria."""
    out = {}
    for c in chaves:
        a = np.array([m1[c][k] for k in sorted(m1[c])])
        b = np.array([m2[c][k] for k in sorted(m1[c])])
        escala = np.max(np.abs(a)) if np.max(np.abs(a)) > 0 else 1.0
        out[c] = float(np.max(np.abs(a - b)) / escala)
    return out
